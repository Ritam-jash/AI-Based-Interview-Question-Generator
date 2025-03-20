import fitz  # PyMuPDF
import re

def extract_text_from_pdf(file_path):
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

def extract_sections(text):
    """
    Extract common resume sections from text.
    
    Args:
        text (str): The text content of the resume
        
    Returns:
        dict: Dictionary with section names as keys and section content as values
    """
    # Common section headers in resumes
    section_patterns = {
        "personal_info": r"(?i)(personal\s+information|contact\s+information|profile)",
        "summary": r"(?i)(summary|professional\s+summary|profile|objective)",
        "education": r"(?i)(education|academic\s+background|qualifications)",
        "experience": r"(?i)(experience|work\s+experience|employment\s+history|work\s+history)",
        "skills": r"(?i)(skills|technical\s+skills|core\s+competencies|expertise)",
        "projects": r"(?i)(projects|personal\s+projects|professional\s+projects)",
        "certifications": r"(?i)(certifications|certificates|credentials)",
        "awards": r"(?i)(awards|honors|achievements)",
        "languages": r"(?i)(languages|language\s+proficiency)",
        "interests": r"(?i)(interests|hobbies|activities)"
    }
    
    sections = {}
    
    # Split text into lines
    lines = text.split('\n')
    
    current_section = "unknown"
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line is a section header
        section_found = False
        for section_name, pattern in section_patterns.items():
            if re.match(pattern, line, re.IGNORECASE) and len(line) < 50:  # Section headers are usually short
                # Save current section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = section_name
                current_content = []
                section_found = True
                break
        
        if not section_found:
            current_content.append(line)
    
    # Save the last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def extract_email(text):
    """
    Extract email address from text.
    
    Args:
        text (str): The text to extract from
        
    Returns:
        str: Extracted email address, or empty string if none found
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ""

def extract_phone(text):
    """
    Extract phone number from text.
    
    Args:
        text (str): The text to extract from
        
    Returns:
        str: Extracted phone number, or empty string if none found
    """
    # This pattern captures various phone number formats
    phone_pattern = r'(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else ""

def extract_links(text):
    """
    Extract links (URLs) from text.
    
    Args:
        text (str): The text to extract from
        
    Returns:
        list: List of extracted URLs
    """
    # Pattern to match URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, text)
    
    # Pattern to match LinkedIn URLs without http/https
    linkedin_pattern = r'linkedin\.com/(?:in|company)/[-\w]+'
    linkedin_urls = re.findall(linkedin_pattern, text)
    urls.extend([f"https://{url}" for url in linkedin_urls])
    
    # Pattern to match GitHub URLs without http/https
    github_pattern = r'github\.com/[-\w]+'
    github_urls = re.findall(github_pattern, text)
    urls.extend([f"https://{url}" for url in github_urls])
    
    return list(set(urls))  # Remove duplicates