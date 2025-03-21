import os
import json
import uuid
from datetime import datetime
import pinecone
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from app.config import get_pinecone_api_key, get_pinecone_environment, get_pinecone_index_name, get_openai_api_key
from dotenv import load_dotenv

load_dotenv()

class VectorStorage:
    def __init__(self):
        try:
            # Initialize local storage by default
            self.use_local_storage = True
            self.local_storage_path = "data/questions_storage.json"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.local_storage_path), exist_ok=True)
            
            # Create empty storage file if it doesn't exist
            if not os.path.exists(self.local_storage_path):
                with open(self.local_storage_path, "w") as f:
                    json.dump([], f)
                    
        except Exception as e:
            print(f"Error initializing local storage: {str(e)}")
            raise
    
    def _get_local_storage(self):
        """Get the local storage data"""
        try:
            with open(self.local_storage_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading local storage: {str(e)}")
            return []
    
    def _save_local_storage(self, data):
        """Save data to local storage"""
        try:
            with open(self.local_storage_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving to local storage: {str(e)}")
            raise
    
    def store_questions(self, questions, job_role, experience_level, skills, session_id=None, is_personalized=False):
        """
        Store interview questions in local storage.
        
        Args:
            questions (list): List of interview questions
            job_role (str): The job role
            experience_level (str): Level of experience
            skills (list): List of skills
            session_id (str, optional): Session ID for grouping questions
            is_personalized (bool): Whether the questions are personalized
            
        Returns:
            bool: Success status
        """
        if not questions:
            raise ValueError("No questions provided")
            
        if not job_role or not experience_level or not skills:
            raise ValueError("Missing required parameters")
        
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Get existing data
            data = self._get_local_storage()
            
            # Create new entry
            entry = {
                "job_role": job_role,
                "experience_level": experience_level,
                "skills": skills,
                "session_id": session_id,
                "is_personalized": is_personalized,
                "timestamp": datetime.now().isoformat(),
                "questions": questions
            }
            
            # Add to data
            data.append(entry)
            
            # Save updated data
            self._save_local_storage(data)
            
            return True
            
        except Exception as e:
            print(f"Error storing questions: {str(e)}")
            raise
    
    def search_questions(self, query, limit=10):
        """
        Search for questions based on a query.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of matching results
        """
        if not query:
            raise ValueError("Search query cannot be empty")
            
        try:
            # Get all data
            data = self._get_local_storage()
            
            # Simple text-based search
            query = query.lower()
            results = []
            
            for entry in data:
                # Search in job role, experience level, and skills
                if (query in entry["job_role"].lower() or
                    query in entry["experience_level"].lower() or
                    any(query in skill.lower() for skill in entry["skills"])):
                    results.append(entry)
            
            return results[:limit]
            
        except Exception as e:
            print(f"Error searching questions: {str(e)}")
            return []
    
    def get_recent_sessions(self, limit=5):
        """
        Get the most recent question sessions.
        
        Args:
            limit (int): Maximum number of sessions to return
            
        Returns:
            list: List of recent sessions
        """
        try:
            # Get all data
            data = self._get_local_storage()
            
            # Sort by timestamp and limit
            data.sort(key=lambda x: x["timestamp"], reverse=True)
            return data[:limit]
            
        except Exception as e:
            print(f"Error getting recent sessions: {str(e)}")
            return []