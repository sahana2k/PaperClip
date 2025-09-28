📎 Paperclip: Your all-in one Research Companion 

Paperclip is an inclusive, AI-powered platform designed to lower barriers for students and accelerate workflows for seasoned researchers. For students, it suggests domains, professors, and simplified papers with accessible starter projects. For researchers, it curates datasets, pretrained models, and GitHub code, generating ready-to-run pipelines. The result? Faster, more inclusive research — and a sustainable future by saving compute, time, and energy.

✨ Key Features
Domain Discovery: Helps students find specific research sub-fields within a broad topic.

Paper Summarizer: Fetches and summarizes recent academic papers from ArXiv.

Professor Finder: Locates professors at a specific university based on their research topic.

Dataset & Model Hub: Discovers relevant datasets and pre-trained models from Hugging Face and GitHub.

Starter Code Generator: Creates boilerplate Python code in a Colab-style format to kickstart projects.

Multilingual Support: Translate paper summaries and chat responses into various languages.

Persistent Chat History: Each user's conversation is saved locally in a dedicated SQLite database.

🛠️ Tech Stack
Backend: Python, FastAPI, LangChain

Frontend: HTML, CSS, JavaScript (No frameworks)

LLM Provider: Cohere (Command R)

Database: SQLite for chat history

External APIs: ArXiv, Semantic Scholar, Hugging Face Hub, GitHub

🚀 Getting Started
Follow these instructions to set up and run the project locally.

1. Prerequisites
Python 3.10 or higher

A virtual environment tool (like venv)

Node.js (for live-server, or use the VS Code Live Server extension)

2. Setup and Installation
Clone the repository:

Bash

git clone https://github.com/your-username/paperclip-project.git
cd paperclip-project
Create and activate a Python virtual environment:

Bash

# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
Install the required Python libraries:

Bash

pip install -r requirements.txt
Create the environment file:

Make a copy of .env.example and name it .env.

Open the .env file and add your secret API keys:

Code snippet

COHERE_API_KEY="your-cohere-api-key"
LANGCHAIN_API_KEY="your-langsmith-api-key" # Optional, for tracing
GITHUB_TOKEN="your-github-personal-access-token"
3. How to Run
You need to run the backend and frontend servers in two separate terminals.

Run the Backend Server:

In your first terminal, run the following command from the project's root directory:

Bash

uvicorn app.main:app --reload
The backend will be running at http://127.0.0.1:8000.

Run the Frontend Server:

The easiest method is using the Live Server extension in Visual Studio Code.

Right-click on the index.html file and select "Open with Live Server".

Alternatively, use npx (comes with Node.js):

Bash

npx live-server

Your browser will open to the Paperclip landing page.
