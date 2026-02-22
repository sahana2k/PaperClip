# chatbot_ui.py - Improved & Simplified for User-Friendly Experience
import streamlit as st
import requests
import json
from datetime import datetime
import re
from typing import Optional, Dict, Any

# --- CONFIGURATION ---
BACKEND_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="PaperClip - AI Research Assistant", 
    page_icon="📎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENHANCED CSS WITH BETTER UX ---
def load_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            * {
                font-family: 'Inter', sans-serif;
            }
            
            /* Main app background */
            .stApp {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            }
            
            /* Text colors */
            h1, h2, h3, h4, h5 {
                color: #f1f5f9 !important;
            }
            
            p, span, label {
                color: #cbd5e1 !important;
            }
            
            /* Main header */
            .main-header {
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                padding: 3rem 2rem;
                border-radius: 1.5rem;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 25px 50px -12px rgba(59, 130, 246, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .main-header h1 {
                color: white !important;
                font-size: 3.5rem;
                margin-bottom: 0.5rem;
                font-weight: 800;
            }
            
            .main-header p {
                color: #dbeafe !important;
                font-size: 1.2rem;
                margin: 0;
                font-weight: 500;
            }
            
            /* Status indicators */
            .status-connected {
                background: rgba(34, 197, 94, 0.1);
                border: 2px solid #22c55e;
                color: #22c55e;
            }
            
            .status-disconnected {
                background: rgba(239, 68, 68, 0.1);
                border: 2px solid #ef4444;
                color: #ef4444;
            }
            
            .status-indicator {
                padding: 0.75rem 1rem;
                border-radius: 0.5rem;
                font-weight: 600;
                display: inline-block;
                margin: 0.5rem 0;
            }
            
            /* Feature cards */
            .feature-card {
                background: linear-gradient(135deg, rgba(30, 58, 138, 0.5) 0%, rgba(55, 48, 163, 0.5) 100%);
                padding: 1.5rem;
                border-radius: 1rem;
                border: 1px solid rgba(96, 165, 250, 0.2);
                margin: 1rem 0;
                transition: all 0.3s ease;
            }
            
            .feature-card:hover {
                transform: translateY(-3px);
                background: linear-gradient(135deg, rgba(30, 58, 138, 0.7) 0%, rgba(55, 48, 163, 0.7) 100%);
                border: 1px solid rgba(96, 165, 250, 0.5);
                box-shadow: 0 20px 25px -5px rgba(96, 165, 250, 0.2);
            }
            
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
            }
            
            .feature-card h3 {
                color: #60a5fa !important;
                margin-bottom: 0.5rem;
                font-size: 1.2rem;
            }
            
            .feature-card p {
                color: #cbd5e1 !important;
                margin: 0;
                font-size: 0.9rem;
            }
            
            /* Buttons */
            .stButton > button {
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                color: white;
                border: none;
                border-radius: 0.75rem;
                padding: 0.75rem 2rem;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 20px 25px -5px rgba(59, 130, 246, 0.5);
            }
            
            /* Chat messages */
            .stChatMessage {
                border-radius: 1rem;
                padding: 1rem;
                margin: 0.75rem 0;
            }
            
            [data-testid="stChatMessage"][data-testid-sender="assistant"] {
                background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
                border-left: 4px solid #60a5fa;
            }
            
            [data-testid="stChatMessage"][data-testid-sender="assistant"] p {
                color: #e0e7ff;
            }
            
            [data-testid="stChatMessage"][data-testid-sender="user"] {
                background: linear-gradient(135deg, #3730a3 0%, #5b21b6 100%);
                border-left: 4px solid #a78bfa;
            }
            
            [data-testid="stChatMessage"][data-testid-sender="user"] p {
                color: #f3e8ff;
            }
            
            /* Input styling */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select {
                background-color: #1e293b !important;
                color: #f1f5f9 !important;
                border: 2px solid #334155 !important;
                border-radius: 0.75rem;
                padding: 0.75rem !important;
            }
            
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            /* Sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
            }
            
            /* Success/Error/Warning boxes */
            .stAlert {
                border-radius: 0.75rem;
            }
            
            .stSuccess {
                background-color: rgba(34, 197, 94, 0.1) !important;
                border: 1px solid #22c55e !important;
                color: #22c55e !important;
            }
            
            .stError {
                background-color: rgba(239, 68, 68, 0.1) !important;
                border: 1px solid #ef4444 !important;
                color: #fca5a5 !important;
            }
            
            .stWarning {
                background-color: rgba(251, 146, 60, 0.1) !important;
                border: 1px solid #fb923c !important;
                color: #fed7aa !important;
            }
            
            .stInfo {
                background-color: rgba(59, 130, 246, 0.1) !important;
                border: 1px solid #3b82f6 !important;
                color: #bfdbfe !important;
            }
            
            /* Stat cards */
            .stat-card {
                background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
                padding: 1rem;
                border-radius: 0.75rem;
                text-align: center;
                border: 1px solid rgba(96, 165, 250, 0.2);
            }
            
            .stat-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #60a5fa;
            }
            
            .stat-label {
                color: #94a3b8;
                font-size: 0.8rem;
                margin-top: 0.25rem;
            }
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
                background-color: transparent;
            }
            
            .stTabs [data-baseweb="tab"] {
                background: transparent;
                color: #cbd5e1;
                border-bottom: 2px solid #334155;
                border-radius: 0;
                padding: 1rem;
                font-weight: 600;
            }
            
            .stTabs [aria-selected="true"] {
                border-bottom: 2px solid #3b82f6;
                color: #60a5fa;
                background: transparent;
            }
            
            /* Expander */
            .streamlit-expanderHeader {
                background: transparent;
                border: 1px solid #334155;
                border-radius: 0.75rem;
                padding: 1rem;
                color: #f1f5f9;
            }
        </style>
    """, unsafe_allow_html=True)


# --- SESSION STATE INITIALIZATION ---
def init_session_state():
    defaults = {
        'page': 'landing',
        'user_id': None,
        'messages': [],
        'command_in_progress': None,
        'backend_available': False,
        'last_backend_check': None,
        'research_stats': {
            'papers_searched': 0,
            'professors_found': 0,
            'datasets_discovered': 0,
            'code_generated': 0,
            'total_queries': 0
        },
        'show_help': False,
        'onboarding_complete': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- BACKEND CONNECTION MANAGEMENT ---
@st.cache_data(ttl=10)
def check_backend_health() -> Dict[str, Any]:
    """Check backend health with detailed information"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return {
                'available': True,
                'status': 'Connected',
                'version': data.get('version', 'N/A'),
                'error': None
            }
    except requests.exceptions.Timeout:
        return {'available': False, 'status': 'Timeout', 'error': 'Backend is not responding (timeout)'}
    except requests.exceptions.ConnectionError:
        return {'available': False, 'status': 'Offline', 'error': 'Cannot connect to backend server'}
    except Exception as e:
        return {'available': False, 'status': 'Error', 'error': str(e)}

# --- API FUNCTIONS WITH ROBUST ERROR HANDLING ---
def call_api(prompt: str, command: Optional[str] = None, university: Optional[str] = None, 
             model_name: Optional[str] = None) -> str:
    """Enhanced API call with comprehensive error handling"""
    
    # Check backend first
    health = check_backend_health()
    if not health['available']:
        return f"❌ **Backend Connection Error**\n\n{health['error']}\n\n**Solution:** Please make sure the backend is running:\n```\nuvicorn app.main:app --reload\n```"
    
    payload = {
        "user_id": st.session_state.user_id or "guest",
        "query": prompt, 
        "command": command, 
        "university": university, 
        "model_name": model_name
    }
    
    try:
        with st.spinner('🔄 Processing your request...'):
            response = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=60)
            response.raise_for_status()
            
            # Update stats
            st.session_state.research_stats['total_queries'] += 1
            if command == "paper_summarizer":
                st.session_state.research_stats['papers_searched'] += 1
            elif command == "professor_finder":
                st.session_state.research_stats['professors_found'] += 1
            elif command == "dataset_hub":
                st.session_state.research_stats['datasets_discovered'] += 1
            elif command == "generate_code":
                st.session_state.research_stats['code_generated'] += 1
            
            result = response.json().get("response", "No response found.")
            return result
            
    except requests.exceptions.Timeout:
        return "⏱️ **Request Timeout**\n\nYour request took too long. Try a simpler query or check your internet connection."
    except requests.exceptions.ConnectionError:
        return f"❌ **Connection Error**\n\nCannot reach backend at {BACKEND_URL}. Make sure it's running."
    except requests.exceptions.HTTPError as e:
        return f"❌ **API Error**\n\n{e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"❌ **Unexpected Error**\n\n{str(e)}"

# --- LANDING PAGE ---
def render_landing_page():
    """Modern landing page with onboarding"""
    
    st.markdown("""
        <div class="main-header">
            <h1>📎 PaperClip</h1>
            <p>Your AI-Powered Research Companion</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Backend status
    health = check_backend_health()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if health['available']:
            st.markdown(f"<div class='status-indicator status-connected'>✅ Backend Connected</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='status-indicator status-disconnected'>❌ Backend Offline</div>", unsafe_allow_html=True)
            st.error(f"⚠️ {health['error']}")
    
    st.markdown("---")
    
    # CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started", use_container_width=True, type="primary"):
            if not health['available']:
                st.error("Please start the backend first!")
            else:
                st.session_state.page = "username"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features section
    st.markdown("### 🎯 What Can PaperClip Do?")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    features = [
        ("🔍", "Domain Discovery", "Explore emerging research fields and find your perfect niche"),
        ("📚", "Paper Summarizer", "Get AI-powered summaries of research papers in seconds"),
        ("👨‍🏫", "Professor Finder", "Find researchers and experts by field and university"),
        ("📊", "Dataset Hub", "Access curated datasets from trusted sources"),
        ("🤖", "Pretrained Models", "Discover state-of-the-art models for your research"),
        ("💻", "Code Generator", "Generate boilerplate code to jumpstart your project")
    ]
    
    for idx, (icon, title, desc) in enumerate(features):
        with [col1, col2, col3][idx % 3]:
            st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stats section
    st.markdown("### 📈 Platform at a Glance")
    col1, col2, col3, col4 = st.columns(4)
    
    stats = [
        ("1M+", "Research Papers"),
        ("50K+", "Datasets"),
        ("10K+", "Models"),
        ("24/7", "AI Support")
    ]
    
    for col, (value, label) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{value}</div>
                    <div class="stat-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)

# --- USERNAME PAGE ---
def render_username_page():
    """User registration/login with validation"""
    
    st.markdown("""
        <div class="main-header">
            <h1>👋 Welcome!</h1>
            <p>Enter your username to get started</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input(
            "Username", 
            key="username_input", 
            placeholder="researcher_2026",
            label_visibility="collapsed"
        )
        
        st.markdown("""
        <p style='font-size: 0.85rem; color: #94a3b8; margin-top: 0.5rem;'>
        Your username helps us save your chat history and research progress.
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("← Back", use_container_width=True):
                st.session_state.page = "landing"
                st.rerun()
        
        with col_b:
            if st.button("Continue →", use_container_width=True, type="primary"):
                if not username or len(username.strip()) < 3:
                    st.error("⚠️ Username must be at least 3 characters")
                elif len(username) > 20:
                    st.error("⚠️ Username must be less than 20 characters")
                elif not username.replace("_", "").replace("-", "").isalnum():
                    st.error("⚠️ Username can only contain letters, numbers, dash, and underscore")
                else:
                    st.session_state.user_id = username
                    st.session_state.page = "chat"
                    st.session_state.messages = [{
                        "role": "assistant",
                        "content": f"👋 **Welcome {username}!**\n\nI'm PaperClip, your AI research assistant. Here's what I can help with:\n\n"
                                   "📚 **Research Tools:**\n"
                                   "• 🔍 Domain Discovery - Find emerging research areas\n"
                                   "• 📄 Paper Summarizer - Quick paper insights\n"
                                   "• 👨‍🏫 Professor Finder - Find experts in your field\n"
                                   "• 📊 Dataset Hub - Discover datasets\n"
                                   "• 🤖 Pretrained Models - Find ML models\n"
                                   "• 💻 Code Generator - Get starter code\n\n"
                                   "**How to get started:**\n"
                                   "1. Use the tools in the sidebar for specific tasks\n"
                                   "2. Or ask me anything in the chat below\n"
                                   "3. Check your stats to track your research activity\n\n"
                                   "**What would you like to explore?**"
                    }]
                    st.rerun()


# --- CHAT PAGE ---
def render_chat_page():
    """Main chat interface with enhanced UX"""
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 📎 PaperClip Chat")
    with col2:
        health = check_backend_health()
        if health['available']:
            st.markdown("✅ Connected")
        else:
            st.markdown("❌ Offline")
    with col3:
        if st.button("🚪 End Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['research_stats']:
                    del st.session_state[key]
            st.session_state.page = "landing"
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🛠️ Research Tools")
        
        tools = {
            "domain_discovery": ("🔍", "Domain Discovery"),
            "paper_summarizer": ("📚", "Paper Summarizer"),
            "professor_finder": ("👨‍🏫", "Professor Finder"),
            "dataset_hub": ("📊", "Dataset Hub"),
            "pretrained_models": ("🤖", "Pretrained Models"),
            "generate_code": ("💻", "Generate Code")
        }
        
        for cmd_id, (icon, label) in tools.items():
            if st.button(f"{icon} {label}", use_container_width=True, key=f"tool_{cmd_id}"):
                st.session_state.command_in_progress = cmd_id
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Your Activity")
        stats = st.session_state.research_stats
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("📄 Papers", stats['papers_searched'])
            st.metric("👨‍🏫 Professors", stats['professors_found'])
        with col_b:
            st.metric("📊 Datasets", stats['datasets_discovered'])
            st.metric("💻 Code", stats['code_generated'])
        
        st.markdown(f"**Total Queries:** {stats['total_queries']}")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📖 History", "❓ Help"])
    
    with tab1:
        # Chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    content = message["content"]
                    
                    # Handle code blocks
                    if "```python" in content or "```" in content:
                        parts = content.split("```")
                        for i, part in enumerate(parts):
                            if i % 2 == 0:
                                if part.strip():
                                    st.markdown(part)
                            else:
                                lang = "python" if "python" in part[:20] else "plaintext"
                                code = part.replace("python\n", "").replace("javascript\n", "").strip()
                                st.code(code, language=lang)
                    else:
                        st.markdown(content)
        
        # Tool form
        if st.session_state.command_in_progress:
            command = st.session_state.command_in_progress
            
            tool_configs = {
                "domain_discovery": {
                    "title": "🔍 Domain Discovery",
                    "description": "Enter a broad topic to discover specific subfields",
                    "inputs": ["topic"]
                },
                "paper_summarizer": {
                    "title": "📚 Paper Summarizer",
                    "description": "Search for papers on a specific topic and get AI summaries",
                    "inputs": ["topic"]
                },
                "professor_finder": {
                    "title": "👨‍🏫 Professor Finder",
                    "description": "Find professors working on a topic at specific universities",
                    "inputs": ["topic", "university"]
                },
                "dataset_hub": {
                    "title": "📊 Dataset Hub",
                    "description": "Discover datasets related to your research topic",
                    "inputs": ["topic"]
                },
                "pretrained_models": {
                    "title": "🤖 Pretrained Models",
                    "description": "Find pretrained ML models for your task",
                    "inputs": ["topic"]
                },
                "generate_code": {
                    "title": "💻 Code Generator",
                    "description": "Generate starter code for ML models and research projects",
                    "inputs": ["topic", "model_name"]
                }
            }
            
            config = tool_configs.get(command, {})
            st.markdown(f"#### {config.get('title', 'Tool')}")
            st.markdown(config.get('description', ''))
            
            with st.form(key=f"{command}_form"):
                topic = st.text_input("Topic/Query", placeholder="e.g., Natural Language Processing")
                
                university = None
                model_name = None
                
                if "university" in config.get("inputs", []):
                    university = st.text_input("University", placeholder="e.g., Stanford University")
                
                if "model_name" in config.get("inputs", []):
                    model_name = st.text_input("Model Name (optional)", placeholder="e.g., BERT, GPT")
                
                col_x, col_y = st.columns(2)
                with col_x:
                    cancel = st.form_submit_button("❌ Cancel")
                with col_y:
                    submit = st.form_submit_button("✅ Search", type="primary")
                
                if cancel:
                    st.session_state.command_in_progress = None
                    st.rerun()
                
                if submit:
                    if not topic or len(topic.strip()) < 2:
                        st.error("⚠️ Please enter a topic")
                    else:
                        user_msg = f"**Using:** {config.get('title')}\n**Query:** {topic}"
                        if university:
                            user_msg += f"\n**University:** {university}"
                        if model_name:
                            user_msg += f"\n**Model:** {model_name}"
                        
                        st.session_state.messages.append({"role": "user", "content": user_msg})
                        response = call_api(topic, command=command, university=university, model_name=model_name)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.command_in_progress = None
                        st.rerun()
        
        # Free chat input
        if not st.session_state.command_in_progress:
            if prompt := st.chat_input("💭 Ask anything about research..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                response = call_api(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    with tab2:
        # History
        st.markdown("### 📖 Chat History")
        
        if st.session_state.messages:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Messages:** {len(st.session_state.messages)}")
            with col2:
                if st.button("📥 Export"):
                    data = json.dumps(st.session_state.messages, indent=2)
                    st.download_button(
                        label="Download",
                        data=data,
                        file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            st.markdown("---")
            for idx, msg in enumerate(st.session_state.messages):
                icon = "👤" if msg["role"] == "user" else "🤖"
                with st.expander(f"{icon} Message {idx + 1}"):
                    st.markdown(msg["content"])
        else:
            st.info("💡 No chat history yet")
    
    with tab3:
        # Help
        st.markdown("### ❓ Getting Started Guide")
        
        with st.expander("🎯 How to use Domain Discovery", expanded=False):
            st.markdown("""
            **Domain Discovery** helps you explore research areas:
            1. Enter a broad topic (e.g., "Artificial Intelligence")
            2. Get back specific subfields and emerging areas
            3. Great for finding your research niche
            
            **Example:** Type "Machine Learning" → Get Neural Networks, NLP, CV, etc.
            """)
        
        with st.expander("📚 How to use Paper Summarizer", expanded=False):
            st.markdown("""
            **Paper Summarizer** finds and summarizes papers:
            1. Enter your research topic
            2. Get top 3 most relevant papers from ArXiv
            3. See AI-generated summaries
            
            **Example:** Type "Transformer models" → Get latest papers with summaries
            """)
        
        with st.expander("👨‍🏫 How to use Professor Finder", expanded=False):
            st.markdown("""
            **Professor Finder** helps you find experts:
            1. Enter your research topic
            2. Enter the university name
            3. Get professors publishing in that area
            
            **Example:** Topic: "NLP", University: "Stanford" → Get NLP professors
            """)
        
        with st.expander("📊 How to use Dataset Hub", expanded=False):
            st.markdown("""
            **Dataset Hub** finds relevant datasets:
            1. Enter your research topic
            2. Search through HuggingFace datasets
            3. Get download links and descriptions
            
            **Example:** Type "Computer Vision" → Get vision datasets
            """)
        
        with st.expander("🤖 How to use Pretrained Models", expanded=False):
            st.markdown("""
            **Pretrained Models** finds ready-to-use models:
            1. Enter your task (e.g., "sentiment analysis")
            2. Get model recommendations
            3. Ready to fine-tune for your project
            
            **Example:** Type "Translation" → Get translation models
            """)
        
        with st.expander("💻 How to use Code Generator", expanded=False):
            st.markdown("""
            **Code Generator** creates starter code:
            1. Enter your project topic
            2. Optionally specify a model (BERT, ResNet, etc.)
            3. Get boilerplate code to start
            
            **Example:** Topic: "Image Classification", Model: "ResNet" → Get starter code
            """)
        
        st.markdown("---")
        
        with st.expander("🔧 Troubleshooting", expanded=False):
            st.markdown("""
            **Backend is offline?**
            - Make sure `uvicorn app.main:app --reload` is running
            - Check port 8000 is not blocked
            
            **Getting timeout errors?**
            - Try simpler queries
            - Check internet connection
            
            **No results?**
            - Try different keywords
            - Be more specific
            
            **Questions?**
            - Contact support or check the logs
            """)

# --- MAIN APPLICATION ---
def main():
    load_css()
    init_session_state()
    
    if st.session_state.page == "landing":
        render_landing_page()
    elif st.session_state.page == "username":
        render_username_page()
    else:
        render_chat_page()

if __name__ == "__main__":
    main()