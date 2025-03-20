from flask import Blueprint, request, jsonify
from app.question_generator import QuestionGenerator
from app.resume_parser import ResumeParser
from app.vector_storage import VectorStorage
import os
import tempfile

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Initialize components
question_generator = QuestionGenerator()
resume_parser = ResumeParser()
vector_storage = VectorStorage()

@api_bp.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    """API endpoint to generate interview questions"""
    try:
        # Get request data
        data = request.json
        
        # Extract parameters
        job_role = data.get('job_role')
        experience_level = data.get('experience_level')
        skills = data.get('skills', [])
        num_questions = data.get('num_questions', 10)
        question_types = data.get('question_types', ["Technical", "Behavioral"])
        
        # Validate required parameters
        if not job_role or not experience_level:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Generate questions
        questions = question_generator.generate_questions(
            job_role=job_role,
            experience_level=experience_level,
            skills=skills,
            num_questions=num_questions,
            question_types=question_types
        )
        
        if not questions:
            return jsonify({'error': 'Failed to generate questions'}), 500
        
        # Store questions
        vector_storage.store_questions(
            questions=questions,
            job_role=job_role,
            experience_level=experience_level,
            skills=skills
        )
        
        # Return questions
        return jsonify({
            'job_role': job_role,
            'experience_level': experience_level,
            'skills': skills,
            'questions': questions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    """API endpoint to parse a resume and extract skills"""
    try:
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
            temp_path = temp.name
            file.save(temp_path)
        
        # Parse the resume
        resume_text, extracted_skills = resume_parser.parse_resume(temp_path)
        
        # Delete the temporary file
        os.unlink(temp_path)
        
        if not resume_text:
            return jsonify({'error': 'Failed to parse resume'}), 500
        
        # Return extracted data
        return jsonify({
            'skills': extracted_skills,
            'text_preview': resume_text[:500] + '...' if len(resume_text) > 500 else resume_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/generate-personalized-questions', methods=['POST'])
def generate_personalized_questions():
    """API endpoint to generate personalized questions based on resume"""
    try:
        # Get request data
        form_data = request.form
        
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        
        # Extract parameters
        job_role = form_data.get('job_role')
        experience_level = form_data.get('experience_level')
        skills = form_data.get('skills', '').split(',')
        num_questions = int(form_data.get('num_questions', 10))
        question_types = form_data.get('question_types', '').split(',')
        
        # Validate required parameters
        if not job_role or not experience_level:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
            temp_path = temp.name
            file.save(temp_path)
        
        # Parse the resume
        resume_text, extracted_skills = resume_parser.parse_resume(temp_path)
        
        # Delete the temporary file
        os.unlink(temp_path)
        
        if not resume_text:
            return jsonify({'error': 'Failed to parse resume'}), 500
        
        # Generate personalized questions
        questions = question_generator.generate_personalized_questions(
            resume_text=resume_text,
            job_role=job_role,
            experience_level=experience_level,
            skills=skills,
            extracted_skills=extracted_skills,
            num_questions=num_questions,
            question_types=question_types
        )
        
        if not questions:
            return jsonify({'error': 'Failed to generate questions'}), 500
        
        # Store questions
        vector_storage.store_questions(
            questions=questions,
            job_role=job_role,
            experience_level=experience_level,
            skills=skills,
            is_personalized=True
        )
        
        # Return questions
        return jsonify({
            'job_role': job_role,
            'experience_level': experience_level,
            'skills': skills,
            'extracted_skills': extracted_skills,
            'questions': questions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/search-questions', methods=['GET'])
def search_questions():
    """API endpoint to search for questions"""
    try:
        # Get query parameter
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        # Search questions
        results = vector_storage.search_questions(query, limit)
        
        # Return results
        return jsonify({
            'query': query,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500