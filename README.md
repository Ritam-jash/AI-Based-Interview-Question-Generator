# AI-Based Interview Question Generator 🤖

A smart application that generates tailored interview questions based on job roles, experience levels, and skills. Users can also upload their resumes to receive personalized interview preparation questions.

## 🎯 Features

- Generate realistic interview questions based on job role & experience level
- Resume parsing to extract skills & tailor questions to candidate profiles
- Store & retrieve past questions using vector database (Pinecone)
- Interactive user interface built with Streamlit

## 🛠️ Tech Stack

- **Backend:** Python, Flask, LangChain, OpenAI API
- **Frontend:** Streamlit
- **Database:** Pinecone (vector storage)
- **Resume Parsing:** PyMuPDF, pdfplumber
- **Data Processing:** Pandas, FAISS

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key and environment

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-interview-bot.git
   cd ai-interview-bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENV=your_pinecone_environment
   ```

## 🖥️ Usage

1. Start the Streamlit application:
   ```bash
   streamlit run main.py
   ```

2. Open your browser and go to `http://localhost:8501`

3. Enter the job role, experience level, and optionally upload a resume

4. Click "Generate Questions" to receive tailored interview questions

## 📁 Project Structure

```
/ai_interview_bot
├── app/
│   ├── __init__.py         # Flask app initialization
│   ├── routes.py           # API endpoints for Streamlit
│   ├── question_generator.py  # Logic for generating questions
│   ├── resume_parser.py    # Resume text/skills extraction
│   ├── vector_storage.py   # Pinecone/FAISS integration
│   └── config.py           # API keys and configurations
│
├── templates/              # HTML templates (if using Flask)
│
├── static/                 # Static files (CSS, JS)
│
├── utils/                  # Utility functions
│
├── .env                    # Environment variables (not tracked)
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── main.py                 # Streamlit app entry point
└── run.py                  # Application runner
```

## 🌟 Future Enhancements

- Speech-to-text input for hands-free operation
- AI-based answer suggestions for practice
- Mock interview mode with feedback
- Integration with LinkedIn profiles for skill extraction
- Enhanced analytics on question difficulty and relevance

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- OpenAI for providing the GPT models
- Pinecone for vector database capabilities
- Streamlit for the interactive UI framework

---

Built with ❤️ by RITAM JASH