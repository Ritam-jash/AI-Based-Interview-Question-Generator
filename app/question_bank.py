import json
import os
from typing import List, Dict

class QuestionBank:
    def __init__(self):
        self.questions = {
            "Python Developer": {
                "Entry-level": {
                    "Technical": [
                        "What is Python? What are its key features?",
                        "Explain the difference between lists and tuples in Python.",
                        "What is a dictionary in Python? How is it different from a list?",
                        "What are decorators in Python? Give an example.",
                        "Explain the concept of inheritance in Python.",
                        "What is the difference between 'is' and '==' in Python?",
                        "How do you handle exceptions in Python?",
                        "What is the difference between append() and extend() in Python lists?",
                        "Explain the concept of generators in Python.",
                        "What is the purpose of the 'self' parameter in Python classes?"
                    ],
                    "Behavioral": [
                        "Tell me about a time when you had to learn a new programming language or technology.",
                        "How do you handle tight deadlines?",
                        "Describe a challenging problem you solved during your studies or projects.",
                        "How do you stay updated with the latest programming trends?",
                        "Tell me about a project you're most proud of."
                    ]
                },
                "Mid-level": {
                    "Technical": [
                        "Explain the GIL (Global Interpreter Lock) in Python.",
                        "How does memory management work in Python?",
                        "What are metaclasses in Python? When would you use them?",
                        "Explain the difference between multiprocessing and threading in Python.",
                        "How do you optimize Python code for performance?",
                        "What is the purpose of __init__.py files?",
                        "Explain the concept of context managers in Python.",
                        "How do you handle database connections in Python?",
                        "What are the differences between asyncio and threading?",
                        "Explain the concept of decorators with parameters."
                    ],
                    "Behavioral": [
                        "How do you mentor junior developers?",
                        "Describe a time when you had to refactor a large codebase.",
                        "How do you handle disagreements with team members?",
                        "Tell me about a time when you had to make a difficult technical decision.",
                        "How do you ensure code quality in your projects?"
                    ]
                }
            },
            "Data Scientist": {
                "Entry-level": {
                    "Technical": [
                        "What is the difference between supervised and unsupervised learning?",
                        "Explain the concept of overfitting in machine learning.",
                        "What is the purpose of cross-validation?",
                        "How do you handle missing data in a dataset?",
                        "What is the difference between correlation and causation?",
                        "Explain the concept of feature scaling.",
                        "What is the purpose of the train-test split?",
                        "How do you evaluate the performance of a classification model?",
                        "What is the difference between mean, median, and mode?",
                        "Explain the concept of hypothesis testing."
                    ],
                    "Behavioral": [
                        "Tell me about a data analysis project you worked on.",
                        "How do you handle large datasets?",
                        "Describe a time when you had to explain complex statistical concepts to non-technical people.",
                        "How do you stay updated with the latest developments in data science?",
                        "Tell me about a time when you had to deal with messy data."
                    ]
                }
            }
        }
    
    def get_questions(self, job_role: str, experience_level: str, num_questions: int = 10) -> List[str]:
        """
        Get questions from the question bank based on job role and experience level.
        
        Args:
            job_role (str): The job role (e.g., "Python Developer")
            experience_level (str): Level of experience (e.g., "Entry-level")
            num_questions (int): Number of questions to return
            
        Returns:
            list: List of questions
        """
        if job_role not in self.questions:
            job_role = "Python Developer"  # Default to Python Developer if role not found
            
        if experience_level not in self.questions[job_role]:
            experience_level = "Entry-level"  # Default to Entry-level if level not found
            
        questions = []
        for category in ["Technical", "Behavioral"]:
            if category in self.questions[job_role][experience_level]:
                questions.extend(self.questions[job_role][experience_level][category])
        
        return questions[:num_questions] 