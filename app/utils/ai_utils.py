import openai
from app.config import get_openai_api_key

def initialize_openai():
    """Initialize OpenAI API with API key"""
    openai.api_key = get_openai_api_key()

def generate_completion(prompt, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.7):
    """
    Generate text completion using OpenAI API.
    
    Args:
        prompt (str): The prompt text
        model (str): The model to use
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Sampling temperature
        
    Returns:
        str: Generated text
    """
    try:
        # Initialize OpenAI
        initialize_openai()
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract and return text
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating completion: {str(e)}")
        return ""

def extract_keywords(text, max_keywords=10):
    """
    Extract keywords from text using OpenAI API.
    
    Args:
        text (str): The input text
        max_keywords (int): Maximum number of keywords to extract
        
    Returns:
        list: List of extracted keywords
    """
    try:
        # Create prompt
        prompt = f"""
        Extract up to {max_keywords} important keywords from the following text.
        Return only the keywords as a comma-separated list, with no additional text or explanation.
        
        Text:
        {text[:2000]}  # Limit text to avoid token limits
        """
        
        # Generate completion
        result = generate_completion(
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
            temperature=0.3
        )
        
        # Parse keywords
        keywords = [keyword.strip() for keyword in result.split(',')]
        
        return keywords
        
    except Exception as e:
        print(f"Error extracting keywords: {str(e)}")
        return []

def generate_embeddings(text):
    """
    Generate embeddings for text using OpenAI API.
    
    Args:
        text (str): The input text
        
    Returns:
        list: The embedding vector
    """
    try:
        # Initialize OpenAI
        initialize_openai()
        
        # Call OpenAI API
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        
        # Extract and return embedding
        return response['data'][0]['embedding']
        
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return []