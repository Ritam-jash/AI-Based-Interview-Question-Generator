import streamlit as st
import os
import pandas as pd
from app.question_generator import QuestionGenerator
from app.resume_parser import ResumeParser
from app.vector_storage import VectorStorage

# Page configuration
st.set_page_config(
    page_title="AI Interview Question Generator",
    page_icon="🤖",
    layout="wide"
)

# Initialize components
question_generator = QuestionGenerator()
resume_parser = ResumeParser()
vector_storage = VectorStorage()

def main():
    st.title("🚀 AI Interview Question Generator")
    st.markdown("Generate tailored interview questions based on job roles and experience levels.")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Generate Questions", "Upload Resume", "View Saved Questions"])
    
    if page == "Generate Questions":
        generate_questions_page()
    elif page == "Upload Resume":
        upload_resume_page()
    elif page == "View Saved Questions":
        view_saved_questions_page()

def generate_questions_page():
    st.header("Generate Interview Questions")
    
    # Form for job details
    with st.form("job_details_form"):
        job_role = st.text_input("Job Role (e.g., Python Developer, Data Scientist)")
        
        experience_level = st.select_slider(
            "Experience Level",
            options=["Entry-level", "Junior", "Mid-level", "Senior", "Lead/Manager"]
        )
        
        skills = st.multiselect(
            "Select Required Skills",
            options=["Python", "JavaScript", "React", "Node.js", "Data Analysis", 
                     "Machine Learning", "SQL", "AWS", "Docker", "Kubernetes", 
                     "Leadership", "Project Management", "Agile", "DevOps"],
            default=["Python"]
        )
        
        additional_skills = st.text_input("Additional Skills (comma-separated)")
        if additional_skills:
            skills.extend([skill.strip() for skill in additional_skills.split(",")])
        
        num_questions = st.slider("Number of Questions", min_value=5, max_value=20, value=10)
        
        question_types = st.multiselect(
            "Question Types",
            options=["Technical", "Behavioral", "Problem-solving", "Situational"],
            default=["Technical", "Behavioral"]
        )
        
        submit_button = st.form_submit_button("Generate Questions")
    
    if submit_button:
        with st.spinner("Generating questions..."):
            questions = question_generator.generate_questions(
                job_role=job_role,
                experience_level=experience_level,
                skills=skills,
                num_questions=num_questions,
                question_types=question_types
            )
            
            if questions:
                st.success(f"Generated {len(questions)} questions!")
                
                # Save questions to vector storage
                session_id = pd.util.hash_pandas_object(pd.Series([job_role, experience_level, str(skills)])).sum()
                vector_storage.store_questions(
                    questions=questions,
                    job_role=job_role,
                    experience_level=experience_level,
                    skills=skills,
                    session_id=str(session_id)
                )
                
                # Display questions
                display_questions(questions)
                
                # Download option
                questions_text = "\n\n".join([f"Q{i+1}: {q}" for i, q in enumerate(questions)])
                st.download_button(
                    label="Download Questions",
                    data=questions_text,
                    file_name=f"interview_questions_{job_role.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
            else:
                st.error("Failed to generate questions. Please try again.")

def upload_resume_page():
    st.header("Upload Resume for Personalized Questions")
    
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type="pdf")
    
    if uploaded_file is not None:
        with st.spinner("Parsing resume..."):
            # Save the uploaded file temporarily
            temp_file_path = os.path.join("temp", uploaded_file.name)
            os.makedirs("temp", exist_ok=True)
            
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Parse the resume
            resume_text, extracted_skills = resume_parser.parse_resume(temp_file_path)
            
            # Remove temporary file
            os.remove(temp_file_path)
            
            if resume_text:
                st.success("Resume parsed successfully!")
                
                with st.expander("Extracted Skills"):
                    st.write(", ".join(extracted_skills))
                
                # Additional form for customization
                with st.form("resume_customization_form"):
                    job_role = st.text_input("Target Job Role")
                    
                    experience_level = st.select_slider(
                        "Experience Level",
                        options=["Entry-level", "Junior", "Mid-level", "Senior", "Lead/Manager"]
                    )
                    
                    # Pre-fill skills from resume
                    skills = st.multiselect(
                        "Skills (extracted from resume, you can modify)",
                        options=["Python", "JavaScript", "React", "Node.js", "Data Analysis", 
                                 "Machine Learning", "SQL", "AWS", "Docker", "Kubernetes", 
                                 "Leadership", "Project Management", "Agile", "DevOps"],
                        default=[skill for skill in extracted_skills if skill in ["Python", "JavaScript", "React", "Node.js", "Data Analysis", 
                                                                                "Machine Learning", "SQL", "AWS", "Docker", "Kubernetes", 
                                                                                "Leadership", "Project Management", "Agile", "DevOps"]]
                    )
                    
                    num_questions = st.slider("Number of Questions", min_value=5, max_value=20, value=10)
                    
                    question_types = st.multiselect(
                        "Question Types",
                        options=["Technical", "Behavioral", "Problem-solving", "Situational"],
                        default=["Technical", "Behavioral"]
                    )
                    
                    submit_button = st.form_submit_button("Generate Personalized Questions")
                
                if submit_button:
                    with st.spinner("Generating personalized questions..."):
                        questions = question_generator.generate_personalized_questions(
                            resume_text=resume_text,
                            job_role=job_role,
                            experience_level=experience_level,
                            skills=skills,
                            extracted_skills=extracted_skills,
                            num_questions=num_questions,
                            question_types=question_types
                        )
                        
                        if questions:
                            st.success(f"Generated {len(questions)} personalized questions!")
                            
                            # Save questions to vector storage
                            session_id = pd.util.hash_pandas_object(pd.Series([job_role, experience_level, str(skills)])).sum()
                            vector_storage.store_questions(
                                questions=questions,
                                job_role=job_role,
                                experience_level=experience_level,
                                skills=skills,
                                session_id=str(session_id),
                                is_personalized=True
                            )
                            
                            # Display questions
                            display_questions(questions)
                            
                            # Download option
                            questions_text = "\n\n".join([f"Q{i+1}: {q}" for i, q in enumerate(questions)])
                            st.download_button(
                                label="Download Questions",
                                data=questions_text,
                                file_name=f"personalized_interview_questions_{job_role.replace(' ', '_')}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error("Failed to generate questions. Please try again.")
            else:
                st.error("Failed to parse resume. Please ensure it's a valid PDF file.")

def view_saved_questions_page():
    st.header("View Saved Questions")
    
    # Search form
    with st.form("search_form"):
        search_query = st.text_input("Search by job role, skills, or keywords")
        submit_search = st.form_submit_button("Search")
    
    if submit_search and search_query:
        with st.spinner("Searching..."):
            results = vector_storage.search_questions(search_query)
            
            if results:
                st.success(f"Found {len(results)} results!")
                
                for i, result in enumerate(results):
                    with st.expander(f"Result {i+1}: {result['job_role']} ({result['experience_level']})"):
                        st.write(f"**Skills:** {', '.join(result['skills'])}")
                        st.write(f"**Generated on:** {result['timestamp']}")
                        st.write("**Questions:**")
                        for j, question in enumerate(result['questions']):
                            st.write(f"{j+1}. {question}")
            else:
                st.info("No matching questions found.")
    
    # List recent sessions
    st.subheader("Recent Question Sets")
    recent_sessions = vector_storage.get_recent_sessions(limit=5)
    
    if recent_sessions:
        for i, session in enumerate(recent_sessions):
            with st.expander(f"{session['job_role']} ({session['experience_level']}) - {session['timestamp']}"):
                st.write(f"**Skills:** {', '.join(session['skills'])}")
                st.write("**Questions:**")
                for j, question in enumerate(session['questions']):
                    st.write(f"{j+1}. {question}")
    else:
        st.info("No saved question sets found.")

def display_questions(questions):
    for i, question in enumerate(questions):
        with st.expander(f"Question {i+1}"):
            st.write(question)

if __name__ == "__main__":
    main()