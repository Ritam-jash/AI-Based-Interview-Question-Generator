# AI Interview Question Generator

An intelligent interview preparation tool that generates personalized technical and behavioral questions based on job roles, skills, and experience levels.

## 🌟 Features

- Dynamic question generation using OpenAI GPT
- Role-specific question templates
- Resume-based question customization
- Mix of technical and behavioral questions
- Dark mode UI with professional design
- Fallback to local question bank when needed

## 🔧 Project Structure

```
ai_interview_bot/
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── app/
│   ├── __init__.py        # Package initialization
│   ├── question_generator.py   # Question generation logic
│   ├── vector_storage.py      # Vector storage handling
│   ├── resume_parser.py       # Resume parsing functionality
│   ├── models.py             # Data models and schemas
│   └── config.py             # Application configuration
├── utils/
│   ├── __init__.py          # Utils package initialization
│   ├── text_processing.py    # Text processing utilities
│   ├── file_handler.py       # File handling utilities
│   ├── api_wrapper.py        # API interaction utilities
│   └── error_handler.py      # Error handling utilities
├
├── streamlit_app.py          # Main application file
├── requirements.txt          # Project dependencies
├── runtime.txt              # Python version specification
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore configuration
└── LICENSE                 # Project license file
```

## 🚀 Setup & Installation

1. Clone the repository:
```bash
git clone https://github.com/Ritam-jash/AI-Based-Interview-Question-Generator
cd ai_interview_bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name
```

## 🎯 Running the Application

1. Local Development:
```bash
streamlit run streamlit_app.py
```

2. Access the application:
- Open your browser and go to `http://localhost:8501`

## 🌐 Deployment

The application is deployed on Streamlit Cloud:
[Add your Streamlit Cloud URL here]

## 💡 Usage

1. Select your target job role
2. Enter your experience level and skills
3. (Optional) Upload your resume for personalized questions
4. Get customized interview questions
5. Practice and prepare!

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- OpenAI for GPT API
- Streamlit for the web framework
- All contributors and users of this project
