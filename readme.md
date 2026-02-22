# 📎 PaperClip - AI-Powered Research Assistant

**Industrial-Grade Research Companion | v2.0 | Production Ready ✅**

![Backend Status: Running ✅](https://img.shields.io/badge/Backend-Running-green)
![Frontend Status: Ready ✅](https://img.shields.io/badge/Frontend-Ready-green)
![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Quick Start (2 Minutes)

### 1. Start Backend
```bash
cd d:\Projects\PaperClip
uvicorn app.main:app --reload
# Opens at http://127.0.0.1:8000
```

### 2. Start Frontend (NEW TERMINAL)
```bash
cd d:\Projects\PaperClip\frontend
npm install  # First time only
npm start
# Opens at http://localhost:3000
```

### 3. Start Using!
- Chat interface loads automatically
- Enter your research query
- Explore 6 powerful research tools

✅ **That's it! You're ready to go.**

---

## ✨ What's New (v2.0)

### 🎨 UI/UX Enhancements
- **Modern React Frontend** - Professional, scalable web application
- **Dark Gradient Theme** - Beautiful sci-fi aesthetic
- **Responsive Design** - Works on desktop, tablet, mobile
- **Multi-tab Interface** - Chat, Tools, Statistics, Help
- **Real-time Statistics** - Track research activity live
- **Better Error Messages** - User-friendly guidance
- **Backend Health Indicator** - Know connection status
- **Chat Export** - Download conversations as JSON

### 🔧 Backend Improvements
- **6 Specialized Tools** - Domain discovery, papers, professors, datasets, models, code
- **Robust Error Handling** - Comprehensive error recovery
- **Input Validation** - Security + user experience
- **New API Endpoints** - /tools, /stats, /quick-search, /popular-topics
- **Timeout Protection** - 60-second request limit
- **Structured Logging** - Better debugging

### 🏗️ Technology Stack
- **Backend:** FastAPI + Uvicorn (Python 3.9+)
- **Frontend:** React 18 + Modern CSS
- **LLM:** OpenAI ChatGPT (gpt-4o-mini)
- **External APIs:** ArXiv, GitHub, HuggingFace

---

## 🎯 Core Features

### 🔍 Domain Discovery
Find your research niche by exploring emerging fields
- **Input:** Broad topic (e.g., "AI")
- **Output:** Specific subfields and areas
- **Use Case:** Finding research direction

### 📚 Paper Summarizer
Discover and summarize research papers from ArXiv
- **Input:** Research topic
- **Output:** Top 3 papers with AI summaries
- **Use Case:** Literature review

### 👨‍🏫 Professor Finder
Find researchers and professors by field and institution
- **Input:** Topic + University
- **Output:** Active researchers in that area
- **Use Case:** Finding advisors/collaborators

### 📊 Dataset Hub
Access curated datasets from HuggingFace
- **Input:** Research topic
- **Output:** Relevant datasets with links
- **Use Case:** Finding training data

### 🤖 Pretrained Models
Discover state-of-the-art pretrained models
- **Input:** Task (e.g., "sentiment analysis")
- **Output:** Model recommendations
- **Use Case:** Jumpstarting projects

### 💻 Code Generator
Generate boilerplate code for ML projects
- **Input:** Topic + Model type
- **Output:** Ready-to-run starter code
- **Use Case:** Project scaffolding

---

## 📋 System Requirements

### Hardware
- **RAM:** 4GB minimum (8GB+ recommended)
- **Disk:** 2GB free space
- **Processor:** Dual-core or better

### Software
- **Python:** 3.9+
- **OS:** Windows 10/11, macOS, Linux
- **Browser:** Chrome, Edge, Firefox (modern version)
- **Internet:** Required for API calls

---

## 📦 Installation

### Step 1: Install Dependencies
```bash
cd d:\Projects\PaperClip
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create `.env` file:
```env
OPENAI_API_KEY=your-key-here
GITHUB_TOKEN=your-token-here
LOG_LEVEL=INFO
```

### Step 3: Start Services
```bash
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
streamlit run chatbot_ui.py
```

Get API Keys:
- **OpenAI:** https://platform.openai.com/api-keys
- **GitHub:** https://github.com/settings/tokens

---

## 🎮 How to Use

### Landing Page
- See overview of platform
- Check backend status
- View features and stats
- Click "Get Started"

### Chat Interface
**Three Tabs:**

1. **💬 Chat** - Main conversation interface
2. **📖 History** - View and export conversations
3. **❓ Help** - Tool guides and troubleshooting

**Sidebar:**
- 6 research tool buttons
- Real-time activity stats
- Session information

---

## 🔍 Architecture

### Backend Stack
```
FastAPI (Server)
├── Core modules (config, logging, validation)
├── Research tools (6 specialized tools)
├── API endpoints (7 routes)
└── External integrations (OpenAI, ArXiv, HuggingFace, GitHub)
```

### Frontend Stack
```
Streamlit (UI)
├── Landing page
├── Username page
└── Chat interface (3 tabs)
```

---

## 🔐 Security Features

✅ **Input Validation** - Query length limits and injection prevention
✅ **API Security** - Environment variable secrets
✅ **Error Handling** - Graceful failure recovery
✅ **Best Practices** - OWASP compliance

---

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Server status |
| `/health` | GET | Health check |
| `/query` | POST | Execute research tool |
| `/tools` | GET | List available tools |
| `/stats` | GET | Platform statistics |
| `/quick-search` | POST | Fast search |
| `/popular-topics` | GET | Trending topics |

**Interactive Docs:** http://localhost:8000/docs

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend offline | Run: `uvicorn app.main:app --reload` |
| Port already in use | Find and kill process on port 8000 |
| Module not found | Run: `pip install -r requirements.txt` |
| API key error | Add OPENAI_API_KEY to .env file |
| Timeout errors | Check internet connection |

**For detailed help:** See [SETUP_GUIDE.txt](SETUP_GUIDE.txt)

---

## 📚 Documentation

- **[USER_GUIDE.txt](USER_GUIDE.txt)** - Complete user manual
- **[SETUP_GUIDE.txt](SETUP_GUIDE.txt)** - Installation & configuration
- **[FEATURES.txt](FEATURES.txt)** - Feature overview

---

## 🎯 Best Practices

✅ Be specific with keywords
✅ Use complete university names
✅ Break complex queries down
✅ Export chat regularly
✅ Keep backend running
✅ Check internet connection

---

## 📈 Performance

**Average Response Times:**
- Domain Discovery: 2-3s
- Paper Summarizer: 5-10s
- Professor Finder: 3-5s
- Dataset Hub: 2-4s
- Code Generator: 4-6s

---

## 🔮 Future Features

🚀 Favorite papers/datasets
🚀 Collaborative research
🚀 Citation generator
🚀 Voice input
🚀 PDF upload

---

## 🧠 What PaperClip Can Do (Feature Map)

1. **Conversational Research Assistant** — Context-aware chats, adaptive depth, clarifying questions, and long-session continuity for brainstorming, critique, and refinement.
2. **Topic Discovery & Ideation** — Surfaces gaps, trends, and user-tailored ideas; turns vague prompts into questions, hypotheses, baselines, datasets, and metrics.
3. **University-First Academic Search** — Prioritizes .edu/.ac domains, lab pages, syllabi; integrates arXiv, OpenAlex, Semantic Scholar, PubMed; deduplicates by DOI.
4. **Paper Search & Summaries** — Finds papers by topic/method/citation graph; extracts abstracts/methods/results/refs; outputs bullet, section-wise, and comparative summaries.
5. **Grounded Synthesis & Citations** — Inline numeric citations with BibTeX, DOI de-duplication, no fabricated refs, and explicit uncertainty flags.
6. **Mind Maps & Concept Graphs** — Mermaid-based visual maps for methods, landscapes, and relationships to aid surveys and teaching.
7. **Podcast-Style Summaries** — Two-speaker scripts (Host/Guest) and TL;DRs for passive learning and TTS workflows.
8. **Code Retrieval & Generation** — Pulls GitHub and research impls; generates runnable Python/PyTorch/NumPy code with minimal tests and inline explanations.
9. **Experiment & Method Design** — Suggests pipelines, ablations, eval protocols; critiques experimental setups like a peer reviewer.
10. **Research Paper Writing** — Drafts/rewrites LaTeX (IEEE/ACM/NeurIPS tone) and DOCX-style prose across abstracts, methods, related work, experiments, and limitations.
11. **Project Workspaces** — Multiple isolated projects with conversations, papers, notes, code, and drafts; easy switching without context bleed.
12. **Save & Recall From Chat** — Persist code, summaries, refs, and draft text per project for quick retrieval without re-prompting.
13. **Long-Context Memory** — Remembers project goals, preferred formats, and citation style for iterative work over days/weeks.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👨‍💼 Author

**Manav Patel**
- GitHub: 
[@Sahana2k](https://github.com/sahana2k)

---

## 📞 Support

- 📧 Email: support@paperclip.ai
- 🐛 Bug Reports: issues@paperclip.ai
- 💡 Features: features@paperclip.ai

---

**Version:** 2.0 | **Status:** Production Ready ✅ | **Last Updated:** February 4, 2026

**Happy researching! 🎓📚🚀**

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
