import os
import json
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from app.config import get_openai_api_key

class QuestionSet(BaseModel):
    questions: List[str] = Field(description="List of interview questions")

class QuestionGenerator:
    def __init__(self):
        # Initialize OpenAI API
        openai.api_key = get_openai_api_key()
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            openai_api_key=get_openai_api_key()
        )
        self.output_parser = PydanticOutputParser(pydantic_object=QuestionSet)
        
    def generate_questions(self, job_role, experience_level, skills, num_questions=10, question_types=None):
        """
        Generate interview questions based on job role, experience level, and skills.
        
        Args:
            job_role (str): The job role (e.g., "Python Developer")
            experience_level (str): Level of experience (e.g., "Entry-level", "Senior")
            skills (list): List of skills relevant to the job
            num_questions (int): Number of questions to generate
            question_types (list): Types of questions to generate (e.g., "Technical", "Behavioral")
            
        Returns:
            list: List of generated questions
        """
        if question_types is None:
            question_types = ["Technical", "Behavioral"]
        
        # Prepare the prompt
        prompt_template = """
        You are an expert technical interviewer with extensive experience in hiring for tech roles.
        
        Please generate {num_questions} interview questions for a {experience_level} {job_role} position.
        
        The candidate should have skills in: {skills_str}.
        
        Question types to include: {question_types_str}.
        
        Guidelines:
        - Make questions specific and relevant to the job role and skills
        - Include a mix of technical and behavioral questions as specified
        - For technical questions, focus on practical application rather than theoretical knowledge
        - For senior roles, include questions about architecture, design decisions, and leadership
        - For junior roles, focus on fundamentals and problem-solving abilities
        - Avoid generic questions that could apply to any role
        - Make sure questions are challenging but fair for the experience level
        
        Return the questions as a JSON list with the following format:
        {format_instructions}
        """
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_template(template=prompt_template)
        
        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Run the chain
        try:
            result = chain.run(
                num_questions=num_questions,
                experience_level=experience_level,
                job_role=job_role,
                skills_str=", ".join(skills),
                question_types_str=", ".join(question_types),
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            # Parse the result
            try:
                # First try parsing as a proper JSON object
                parsed_result = self.output_parser.parse(result)
                return parsed_result.questions
            except Exception as e:
                # If parsing fails, try to extract the JSON from the text
                try:
                    # Look for JSON-like structure in the text
                    start_idx = result.find('{')
                    end_idx = result.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = result[start_idx:end_idx]
                        parsed_json = json.loads(json_str)
                        if "questions" in parsed_json:
                            return parsed_json["questions"]
                except:
                    pass
                
                # If all else fails, just split by newlines and clean up
                questions = [q.strip() for q in result.split('\n') if q.strip()]
                questions = [q.replace("- ", "", 1) if q.startswith("- ") else q for q in questions]
                questions = [q.lstrip("0123456789. ") for q in questions]
                return questions[:num_questions]
                
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return []
    
    def generate_personalized_questions(self, resume_text, job_role, experience_level, skills, 
                                        extracted_skills, num_questions=10, question_types=None):
        """
        Generate personalized interview questions based on a resume and job details.
        
        Args:
            resume_text (str): The text content of the resume
            job_role (str): The job role the candidate is applying for
            experience_level (str): Level of experience (e.g., "Entry-level", "Senior")
            skills (list): List of skills relevant to the job
            extracted_skills (list): Skills extracted from the resume
            num_questions (int): Number of questions to generate
            question_types (list): Types of questions to generate (e.g., "Technical", "Behavioral")
            
        Returns:
            list: List of generated questions
        """
        if question_types is None:
            question_types = ["Technical", "Behavioral"]
        
        # Prepare the prompt
        prompt_template = """
        You are an expert technical interviewer with extensive experience in hiring for tech roles.
        
        Please generate {num_questions} personalized interview questions for a candidate applying for a {experience_level} {job_role} position.
        
        The job requires skills in: {skills_str}.
        
        Here is the candidate's resume:
        ```
        {resume_text}
        ```
        
        From their resume, I've extracted these skills: {extracted_skills_str}.
        
        Question types to include: {question_types_str}.
        
        Guidelines:
        - Tailor questions to the candidate's specific experience and skills mentioned in their resume
        - Focus on areas where the candidate's experience aligns with the job requirements
        - Ask about specific projects or achievements mentioned in the resume
        - Include questions that assess both technical knowledge and practical application
        - For areas where the candidate may lack direct experience but the job requires it, ask how they would approach learning or adapting
        - Include a mix of technical and behavioral questions as specified
        - Make questions challenging but fair for the experience level
        
        Return the questions as a JSON list with the following format:
        {format_instructions}
        """
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_template(template=prompt_template)
        
        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Run the chain
        try:
            result = chain.run(
                num_questions=num_questions,
                experience_level=experience_level,
                job_role=job_role,
                skills_str=", ".join(skills),
                resume_text=resume_text[:3000],  # Limit resume text to avoid token limits
                extracted_skills_str=", ".join(extracted_skills),
                question_types_str=", ".join(question_types),
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            # Parse the result
            try:
                # First try parsing as a proper JSON object
                parsed_result = self.output_parser.parse(result)
                return parsed_result.questions
            except Exception as e:
                # If parsing fails, try to extract the JSON from the text
                try:
                    # Look for JSON-like structure in the text
                    start_idx = result.find('{')
                    end_idx = result.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = result[start_idx:end_idx]
                        parsed_json = json.loads(json_str)
                        if "questions" in parsed_json:
                            return parsed_json["questions"]
                except:
                    pass
                
                # If all else fails, just split by newlines and clean up
                questions = [q.strip() for q in result.split('\n') if q.strip()]
                questions = [q.replace("- ", "", 1) if q.startswith("- ") else q for q in questions]
                questions = [q.lstrip("0123456789. ") for q in questions]
                return questions[:num_questions]
                
        except Exception as e:
            print(f"Error generating personalized questions: {str(e)}")
            return []