import os
import json
from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.question_bank import QuestionBank
from dotenv import load_dotenv
import time
import logging
import openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class QuestionSet(BaseModel):
    questions: List[str] = Field(description="List of interview questions")

class QuestionGenerator:
    def __init__(self):
        try:
            # Initialize local question bank
            self.question_bank = QuestionBank()
            
            # Initialize OpenAI API
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                # Validate API key format
                if not openai_api_key.startswith("sk-"):
                    logger.warning("Invalid OpenAI API key format. Using local question bank only.")
                    self.use_api = False
                else:
                    try:
                        # Test the API key
                        openai.api_key = openai_api_key
                        openai.models.list()  # This will fail if the key is invalid
                        
                        logger.info("Initializing OpenAI API with GPT-3.5-turbo")
                        self.llm = ChatOpenAI(
                            model_name="gpt-3.5-turbo",
                            temperature=0.7,
                            openai_api_key=openai_api_key,
                            max_retries=3,
                            request_timeout=30
                        )
                        self.output_parser = PydanticOutputParser(pydantic_object=QuestionSet)
                        self.use_api = True
                        self.last_api_call = 0
                        self.min_delay = 2  # Increased delay to respect rate limits
                        self.api_key_valid = True
                    except Exception as e:
                        logger.error(f"Invalid OpenAI API key: {str(e)}")
                        self.use_api = False
                        self.api_key_valid = False
            else:
                logger.warning("No OpenAI API key found. Using local question bank only.")
                self.use_api = False
                self.api_key_valid = False
                
        except Exception as e:
            logger.error(f"Error initializing QuestionGenerator: {str(e)}")
            self.use_api = False
            self.api_key_valid = False
            self.question_bank = QuestionBank()
    
    def _wait_for_rate_limit(self):
        """Wait if needed to respect rate limits"""
        if self.use_api and self.api_key_valid:
            current_time = time.time()
            time_since_last_call = current_time - self.last_api_call
            if time_since_last_call < self.min_delay:
                time.sleep(self.min_delay - time_since_last_call)
            self.last_api_call = time.time()
        
    def generate_questions(self, job_role, experience_level, skills, num_questions=10, question_types=None):
        """
        Generate interview questions based on job role, experience level, and skills.
        Falls back to local question bank if API is not available or quota is exceeded.
        """
        logger.info(f"Generating questions for {job_role} ({experience_level})")
        
        if not job_role or not experience_level or not skills:
            logger.error("Missing required parameters")
            raise ValueError("Missing required parameters")
            
        if num_questions < 1 or num_questions > 50:
            logger.error(f"Invalid number of questions: {num_questions}")
            raise ValueError("Number of questions must be between 1 and 50")
            
        try:
            # Try using API if available and valid
            if self.use_api and self.api_key_valid:
                try:
                    self._wait_for_rate_limit()
                    
                    # Prepare the prompt with more specific instructions
                    prompt_template = """
                    Generate {num_questions} interview questions for a {experience_level} {job_role} position.
                    Required skills: {skills_str}
                    
                    Rules:
                    1. Questions must be specific to {job_role} and the required skills
                    2. Mix of technical (70%) and behavioral (30%) questions
                    3. Technical questions should focus on practical application
                    4. Questions should be challenging but fair for {experience_level}
                    5. Avoid generic questions that could apply to any role
                    6. Each question should be unique and specific
                    
                    Format: Return as a JSON list of questions.
                    """
                    
                    # Create the prompt
                    prompt = ChatPromptTemplate.from_template(template=prompt_template)
                    
                    # Create the chain
                    chain = LLMChain(llm=self.llm, prompt=prompt)
                    
                    # Run the chain
                    logger.info("Making API call to generate questions")
                    result = chain.run(
                        num_questions=num_questions,
                        experience_level=experience_level,
                        job_role=job_role,
                        skills_str=", ".join(skills)
                    )
                    
                    # Parse the result
                    try:
                        # Try to extract questions from the response
                        if isinstance(result, str):
                            logger.info("Processing API response")
                            # Look for JSON-like structure
                            start_idx = result.find('[')
                            end_idx = result.rfind(']') + 1
                            if start_idx >= 0 and end_idx > start_idx:
                                json_str = result[start_idx:end_idx]
                                questions = json.loads(json_str)
                                if isinstance(questions, list) and all(isinstance(q, str) for q in questions):
                                    logger.info(f"Successfully generated {len(questions)} questions")
                                    return questions[:num_questions]
                            
                            # If no JSON found, try to extract questions from text
                            questions = [q.strip() for q in result.split('\n') if q.strip()]
                            questions = [q.replace("- ", "").replace("1.", "").replace("2.", "").replace("3.", "").replace("4.", "").replace("5.", "") for q in questions]
                            questions = [q.strip() for q in questions if q.strip()]
                            logger.info(f"Successfully extracted {len(questions)} questions from text")
                            return questions[:num_questions]
                            
                    except Exception as e:
                        logger.error(f"Error parsing API response: {str(e)}")
                        logger.info("Falling back to local questions")
                        return self._get_local_questions(job_role, experience_level, num_questions)
                        
                except Exception as e:
                    logger.error(f"API error: {str(e)}")
                    logger.info("Falling back to local questions")
                    return self._get_local_questions(job_role, experience_level, num_questions)
            else:
                logger.info("API not available or invalid, using local questions")
                return self._get_local_questions(job_role, experience_level, num_questions)
                
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise    
    def _get_local_questions(self, job_role, experience_level, num_questions):
        """Get questions from the local question bank"""
        logger.info(f"Getting local questions for {job_role} ({experience_level})")
        try:
            questions = self.question_bank.get_questions(
                job_role=job_role,
                experience_level=experience_level,
                num_questions=num_questions
            )
            logger.info(f"Successfully retrieved {len(questions)} local questions")
            return questions
        except Exception as e:
            logger.error(f"Error getting local questions: {str(e)}")
            # Return some default questions if local bank fails
            return [
                f"Tell me about your experience with {job_role}.",
                f"What are your key strengths as a {experience_level} {job_role}?",
                f"Describe a challenging project you worked on as a {job_role}.",
                f"How do you stay updated with the latest {job_role} technologies?",
                f"What tools and frameworks do you use in your {job_role} work?"
            ]
    
    def generate_personalized_questions(self, resume_text, job_role, experience_level, skills, 
                                     extracted_skills, num_questions=10, question_types=None):
        """
        Generate personalized interview questions based on a resume and job details.
        Falls back to local question bank if API is not available or quota is exceeded.
        """
        if not resume_text or not job_role or not experience_level or not skills:
            raise ValueError("Missing required parameters")
            
        if num_questions < 1 or num_questions > 50:
            raise ValueError("Number of questions must be between 1 and 50")
            
        try:
            # Try using API if available
            if self.use_api:
                try:
                    self._wait_for_rate_limit()
                    
                    # Prepare the prompt with more specific instructions
                    prompt_template = """
                    Generate {num_questions} personalized interview questions for a {experience_level} {job_role} position.
                    
                    Job Requirements:
                    - Required skills: {skills_str}
                    
                    Candidate Profile:
                    - Resume: {resume_text}
                    - Extracted skills: {extracted_skills_str}
                    
                    Rules:
                    1. Questions must be specific to the candidate's experience and skills
                    2. Focus on areas where candidate's experience matches job requirements
                    3. Ask about specific projects/achievements from their resume
                    4. Mix of technical (70%) and behavioral (30%) questions
                    5. Questions should be challenging but fair for {experience_level}
                    6. Each question should be unique and personalized
                    
                    Format: Return as a JSON list of questions.
                    """
                    
                    # Create the prompt
                    prompt = ChatPromptTemplate.from_template(template=prompt_template)
                    
                    # Create the chain
                    chain = LLMChain(llm=self.llm, prompt=prompt)
                    
                    # Run the chain
                    result = chain.run(
                        num_questions=num_questions,
                        experience_level=experience_level,
                        job_role=job_role,
                        skills_str=", ".join(skills),
                        resume_text=resume_text[:2000],  # Limit resume text
                        extracted_skills_str=", ".join(extracted_skills)
                    )
                    
                    # Parse the result
                    try:
                        # Try to extract questions from the response
                        if isinstance(result, str):
                            # Look for JSON-like structure
                            start_idx = result.find('[')
                            end_idx = result.rfind(']') + 1
                            if start_idx >= 0 and end_idx > start_idx:
                                json_str = result[start_idx:end_idx]
                                questions = json.loads(json_str)
                                if isinstance(questions, list) and all(isinstance(q, str) for q in questions):
                                    return questions[:num_questions]
                            
                            # If no JSON found, try to extract questions from text
                            questions = [q.strip() for q in result.split('\n') if q.strip()]
                            questions = [q.replace("- ", "").replace("1.", "").replace("2.", "").replace("3.", "").replace("4.", "").replace("5.", "") for q in questions]
                            questions = [q.strip() for q in questions if q.strip()]
                            return questions[:num_questions]
                            
                    except Exception as e:
                        print(f"Error parsing API response: {str(e)}")
                        return self._get_local_questions(job_role, experience_level, num_questions)
                        
                except Exception as e:
                    print(f"API error: {str(e)}. Falling back to local questions.")
                    return self._get_local_questions(job_role, experience_level, num_questions)
            else:
                # Use local questions if API is not available
                return self._get_local_questions(job_role, experience_level, num_questions)
                
        except Exception as e:
            print(f"Error generating personalized questions: {str(e)}")
            raise
