import os
import re
import fitz  # PyMuPDF
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from app.config import get_openai_api_key

class ResumeParser:
    def __init__(self):
        # Initialize OpenAI API
        openai.api_key = get_openai_api_key()
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.2,
            openai_api_key=get_openai_api_key()
        )
        
        # Common technical skills for extraction
        self.common_skills = [
            # Programming Languages
            "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "Go", "Rust", "Swift", "Kotlin",
            "PHP", "TypeScript", "Scala", "R", "MATLAB", "Perl", "Shell", "Bash", "PowerShell",
            
            # Web Development
            "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask",
            "Ruby on Rails", "Spring Boot", "ASP.NET", "Laravel", "jQuery", "Bootstrap", "Tailwind CSS",
            
            # Data Science & ML
            "Machine Learning", "Deep Learning", "Data Science", "TensorFlow", "PyTorch", "Keras",
            "scikit-learn", "pandas", "NumPy", "Data Analysis", "Data Visualization", "Statistical Analysis",
            "Natural Language Processing", "Computer Vision", "Reinforcement Learning",
            
            # Database
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Microsoft SQL Server",
            "NoSQL", "Redis", "Cassandra", "DynamoDB", "Firebase", "Elasticsearch",
            
            # Cloud & DevOps
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "CI/CD", "Jenkins", "GitLab CI",
            "GitHub Actions", "Terraform", "Ansible", "Chef", "Puppet", "Prometheus", "Grafana",
            
            # Other Technical Skills
            "Git", "RESTful APIs", "GraphQL", "Microservices", "Serverless", "Linux", "Unix",
            "Big Data", "Apache Spark", "Hadoop", "Tableau", "Power BI", "Agile", "Scrum",
            "Jira", "Confluence", "DevOps", "Site Reliability Engineering", "System Design",
            
            # Soft Skills
            "Project Management", "Team Leadership", "Communication", "Problem-solving", "Agile Methodology",
            "Critical Thinking", "Time Management", "Teamwork", "Collaboration", "Adaptability"
        ]
    
    def parse_resume(self, file_path):
        """
        Parse a resume PDF file and extract text and skills.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            tuple: (resume_text, extracted_skills)
        """
        try:
            # Extract text from PDF
            resume_text = self._extract_text_from_pdf(file_path)
            
            if not resume_text:
                return None, []
            
            # Extract skills using both pattern matching and AI
            extracted_skills = self._extract_skills(resume_text)
            
            return resume_text, extracted_skills
            
        except Exception as e:
            print(f"Error parsing resume: {str(e)}")
            return None, []
    
    def _extract_text_from_pdf(self, file_path):
        """
        Extract text from a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            text = ""
            
            # Open the PDF file
            with fitz.open(file_path) as pdf:
                # Iterate through each page
                for page in pdf:
                    # Extract text from the page
                    text += page.get_text()
            
            return text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _extract_skills(self, resume_text):
        """
        Extract skills from resume text using pattern matching and AI.
        
        Args:
            resume_text (str): The text content of the resume
            
        Returns:
            list: List of extracted skills
        """
        # Extract skills using pattern matching
        pattern_skills = self._extract_skills_by_pattern(resume_text)
        
        # Extract skills using AI
        ai_skills = self._extract_skills_by_ai(resume_text)
        
        # Combine and deduplicate skills
        all_skills = list(set(pattern_skills + ai_skills))
        
        return all_skills
    
    def _extract_skills_by_pattern(self, resume_text):
        """
        Extract skills from resume text using pattern matching.
        
        Args:
            resume_text (str): The text content of the resume
            
        Returns:
            list: List of extracted skills
        """
        skills = []
        
        # Clean and normalize the text
        clean_text = resume_text.lower()
        
        # Check for each skill in the common skills list
        for skill in self.common_skills:
            # Create a regex pattern that matches the skill as a whole word
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, clean_text):
                skills.append(skill)
        
        return skills
    
    def _extract_skills_by_ai(self, resume_text):
        """
        Extract skills from resume text using AI.
        
        Args:
            resume_text (str): The text content of the resume
            
        Returns:
            list: List of extracted skills
        """
        # Prepare the prompt
        prompt_template = """
        You are a skilled resume parser. Extract technical and soft skills from the following resume text.
        
        Resume text:
        ```
        {resume_text}
        ```
        
        Guidelines:
        - Extract both technical skills (programming languages, frameworks, tools) and soft skills (leadership, communication, etc.)
        - Focus on specific skills, not generic descriptions
        - Look for skills in the Skills section, as well as those mentioned in work experience and projects
        - Return a comma-separated list of skills, with no additional text or explanation
        
        Example output: Python, JavaScript, React, AWS, Docker, Project Management, Team Leadership
        """
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_template(template=prompt_template)
        
        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Run the chain
        try:
            result = chain.run(
                resume_text=resume_text[:3000]  # Limit text to avoid token limits
            )
            
            # Parse the comma-separated list
            skills = [skill.strip() for skill in result.split(',')]
            
            return skills
            
        except Exception as e:
            print(f"Error extracting skills using AI: {str(e)}")
            return []