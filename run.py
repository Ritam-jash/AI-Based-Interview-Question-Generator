import os
from app import create_app
import sys
import subprocess

def main():
    """Run the application"""
    # Check for environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set. Please set it in .env file.")
    
    # Create the Flask app
    app = create_app()
    
    # Run the app
    if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
        # Run Streamlit app
        print("Starting Streamlit app...")
        subprocess.run(["streamlit", "run", "main.py"])
    else:
        # Run Flask app
        port = int(os.getenv("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == "__main__":
    main()