import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_api_key():
    """Get OpenAI API key from environment variables"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    return api_key

def get_pinecone_api_key():
    """Get Pinecone API key from environment variables"""
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("Warning: Pinecone API key not found. Local storage will be used as fallback.")
    return api_key

def get_pinecone_environment():
    """Get Pinecone environment from environment variables"""
    env = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    return env

def get_pinecone_index_name():
    """Get Pinecone index name from environment variables"""
    index_name = os.getenv("PINECONE_INDEX_NAME", "interview-questions")
    return index_name