import os
import json
import uuid
from datetime import datetime
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from app.config import get_pinecone_api_key, get_pinecone_environment, get_pinecone_index_name, get_openai_api_key

class VectorStorage:
    def __init__(self):
        self.pinecone_api_key = get_pinecone_api_key()
        self.pinecone_env = get_pinecone_environment()
        self.pinecone_index_name = get_pinecone_index_name()
        self.openai_api_key = get_openai_api_key()
        
        # Initialize Pinecone
        self._initialize_pinecone()
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key
        )
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and ensure index exists"""
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=self.pinecone_api_key,
                environment=self.pinecone_env
            )
            
            # Check if index exists, if not create it
            if self.pinecone_index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.pinecone_index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
                print(f"Created new Pinecone index: {self.pinecone_index_name}")
            
            # Connect to the index
            self.index = pinecone.Index(self.pinecone_index_name)
            
            # Create vectorstore
            self.vectorstore = Pinecone(
                index=self.index,
                embedding=self.embeddings,
                text_key="text"
            )
            
        except Exception as e:
            print(f"Error initializing Pinecone: {str(e)}")
            # Fallback to local storage if Pinecone fails
            self._initialize_local_storage()
    
    def _initialize_local_storage(self):
        """Initialize local storage as a fallback"""
        self.use_local_storage = True
        self.local_storage_path = "data/questions_storage.json"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.local_storage_path), exist_ok=True)
        
        # Create empty storage file if it doesn't exist
        if not os.path.exists(self.local_storage_path):
            with open(self.local_storage_path, "w") as f:
                json.dump([], f)
    
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
    
    def store_questions(self, questions, job_role, experience_level, skills, session_id=None, is_personalized=False):
        """
        Store interview questions in the vector database.
        
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
            return False
        
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Check if we're using local storage
            if hasattr(self, 'use_local_storage') and self.use_local_storage:
                return self._store_questions_locally(
                    questions, job_role, experience_level, skills, session_id, is_personalized
                )
            
            # Create metadata
            metadata = {
                "job_role": job_role,
                "experience_level": experience_level,
                "skills": skills,
                "session_id": session_id,
                "is_personalized": is_personalized,
                "timestamp": datetime.now().isoformat(),
                "questions": questions
            }
            
            # Convert questions to documents
            documents = []
            for i, question in enumerate(questions):
                # Create a document for each question
                doc = Document(
                    page_content=question,
                    metadata={
                        "job_role": job_role,
                        "experience_level": experience_level,
                        "skills": skills,
                        "session_id": session_id,
                        "is_personalized": is_personalized,
                        "timestamp": datetime.now().isoformat(),
                        "question_index": i,
                        "total_questions": len(questions)
                    }
                )
                documents.append(doc)
            
            # Store session metadata
            session_doc = Document(
                page_content=f"Session for {job_role} ({experience_level})",
                metadata=metadata
            )
            documents.append(session_doc)
            
            # Add documents to vectorstore
            self.vectorstore.add_documents(documents)
            
            return True
            
        except Exception as e:
            print(f"Error storing questions in vector database: {str(e)}")
            # Try fallback to local storage
            self._initialize_local_storage()
            return self._store_questions_locally(
                questions, job_role, experience_level, skills, session_id, is_personalized
            )
    
    def _store_questions_locally(self, questions, job_role, experience_level, skills, session_id, is_personalized):
        """Store questions in local storage"""
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
            print(f"Error storing questions locally: {str(e)}")
            return False
    
    def search_questions(self, query, limit=10):
        """
        Search for questions based on a query.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of matching results
        """
        try:
            # Check if we're using local storage
            if hasattr(self, 'use_local_storage') and self.use_local_storage:
                return self._search_questions_locally(query, limit)
            
            # Search in vectorstore
            results = self.vectorstore.similarity_search(
                query,
                k=limit * 2  # Get more results than needed to filter
            )
            
            # Group by session_id
            sessions = {}
            for doc in results:
                session_id = doc.metadata.get("session_id")
                if not session_id:
                    continue
                
                if session_id not in sessions:
                    sessions[session_id] = {
                        "job_role": doc.metadata.get("job_role", ""),
                        "experience_level": doc.metadata.get("experience_level", ""),
                        "skills": doc.metadata.get("skills", []),
                        "is_personalized": doc.metadata.get("is_personalized", False),
                        "timestamp": doc.metadata.get("timestamp", ""),
                        "questions": []
                    }
                
                # Add question if it's not a session document
                if "question_index" in doc.metadata:
                    sessions[session_id]["questions"].append(doc.page_content)
            
            # Get complete question sets
            complete_sessions = []
            for session_id, session in sessions.items():
                # Get complete session data
                try:
                    # Search for session document
                    session_docs = self.vectorstore.similarity_search(
                        f"Session for {session['job_role']} ({session['experience_level']})",
                        filter={"session_id": session_id},
                        k=1
                    )
                    
                    if session_docs:
                        session_doc = session_docs[0]
                        if "questions" in session_doc.metadata:
                            # Use questions from metadata
                            session["questions"] = session_doc.metadata["questions"]
                except:
                    # If we can't get full session, use what we have
                    pass
                
                complete_sessions.append(session)
            
            # Limit results
            return complete_sessions[:limit]
            
        except Exception as e:
            print(f"Error searching questions: {str(e)}")
            # Try fallback to local storage
            if not hasattr(self, 'use_local_storage'):
                self._initialize_local_storage()
            return self._search_questions_locally(query, limit)
    
    def _search_questions_locally(self, query, limit):
        """Search questions in local storage"""
        try:
            # Get existing data
            data = self._get_local_storage()
            
            # Simple text search (basic implementation)
            query = query.lower()
            results = []
            
            for entry in data:
                # Check if query is in job role, skills, or questions
                job_role = entry.get("job_role", "").lower()
                skills = [skill.lower() for skill in entry.get("skills", [])]
                
                match_score = 0
                if query in job_role:
                    match_score += 3
                
                for skill in skills:
                    if query in skill:
                        match_score += 2
                        break
                
                for question in entry.get("questions", []):
                    if query in question.lower():
                        match_score += 1
                
                if match_score > 0:
                    results.append((match_score, entry))
            
            # Sort by match score (descending)
            results.sort(key=lambda x: x[0], reverse=True)
            
            # Return top results
            return [entry for _, entry in results[:limit]]
            
        except Exception as e:
            print(f"Error searching questions locally: {str(e)}")
            return []
    
    def get_recent_sessions(self, limit=5):
        """
        Get recent question sessions.
        
        Args:
            limit (int): Maximum number of sessions to return
            
        Returns:
            list: List of recent sessions
        """
        try:
            # Check if we're using local storage
            if hasattr(self, 'use_local_storage') and self.use_local_storage:
                return self._get_recent_sessions_locally(limit)
            
            # Not implemented for Pinecone yet - fallback to local storage
            self._initialize_local_storage()
            return self._get_recent_sessions_locally(limit)
            
        except Exception as e:
            print(f"Error getting recent sessions: {str(e)}")
            return []
    
    def _get_recent_sessions_locally(self, limit):
        """Get recent sessions from local storage"""
        try:
            # Get existing data
            data = self._get_local_storage()
            
            # Sort by timestamp (descending)
            data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Return top results
            return data[:limit]
            
        except Exception as e:
            print(f"Error getting recent sessions locally: {str(e)}")
            return []