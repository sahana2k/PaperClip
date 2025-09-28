# chatbot_ui.py
import streamlit as st
import requests
import re

# --- CONFIGURATION ---
BACKEND_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="Paperclip", page_icon="📎", layout="centered")

# --- CUSTOM CSS TO MATCH YOUR DESIGN ---
def load_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
            
            html, body, [class*="st-"], button, input {
                font-family: 'Poppins', sans-serif;
            }
            
            /* Main background color */
            .stApp {
                background-color: #37353E;
            }

            /* --- BUTTON STYLES --- */
            .stButton > button {
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
                background-color: #444344E;
                color: white;
                border-radius: 999px;
                padding: 12px 28px;
                border: none;
                transition: background-color 0.2s, transform 0.2s;
            }
            .stButton > button:hover {
                background-color: #37353E;
                color: white;
                transform: scale(1.02);
            }
            
            /* Sidebar tool buttons */
            .stSidebar .stButton > button {
                background-color: #f1f5fb;
                color: #333;
                border: 1px solid #dbeafe;
            }
             .stSidebar .stButton > button:hover {
                background-color: #dbeafe;
                color: #333;
            }

            /* --- LANDING PAGE --- */
            .landing-header {
                font-family: 'Comfortaa', cursive;
                font-weight: 700;
                text-align: center;
                color: white;
            }
            .landing-subheader {
                text-align: center;
                color: white;
            }
            .feature-card {
                background-color: white;
                color: #333;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                height: 170px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            .feature-card h4 {
                 font-family: 'Comfortaa', cursive;
                 font-weight: 700;
                 color: #44444E;
            }
            
            /* --- CHAT PAGE --- */
            /* This is the container for each message bubble */
            .stChatMessage {
                border-radius: 10px;
                border: none;
                padding: 15px;
            }

            /* Assistant messages (white bubble, dark text) */
            [data-testid="stChatMessage"][data-testid-sender="assistant"] {
                 background-color: white; 
            }
            [data-testid="stChatMessage"][data-testid-sender="assistant"] p {
                 color: #333; /* Make text dark */
            }

            /* User messages (dark bubble, white text) */
            [data-testid="stChatMessage"][data-testid-sender="user"] {
                 background-color: #44444E;
            }
            [data-testid="stChatMessage"][data-testid-sender="user"] p {
                 color: white; /* Make text light */
            }
            
        </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "landing"
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'command_in_progress' not in st.session_state:
    st.session_state.command_in_progress = None

# --- API CALL FUNCTION ---
def call_api(prompt, command=None, university=None, model_name=None):
    payload = {"user_id": st.session_state.user_id, "query": prompt, "command": command, "university": university, "model_name": model_name}
    try:
        response = requests.post(f"{BACKEND_URL}/query", json=payload)
        response.raise_for_status()
        return response.json().get("response", "No response found.")
    except requests.exceptions.RequestException as e:
        return f"Connection Error: {e}. Is the backend server running?"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- PAGE RENDERING LOGIC ---

def render_landing_page():
    st.markdown('<h1 class="landing-header">PaperClip</h1>', unsafe_allow_html=True)
    st.markdown('<p class="landing-subheader">Your AI-Powered Research Companion</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Get Started", use_container_width=True):
            st.session_state.page = "username"
            st.rerun()

    st.markdown("---")
    st.subheader("For Students")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="feature-card"><h4>Domain Discovery</h4><p>Find your ideal research area.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="feature-card"><h4>Professor Finder</h4><p>Search professors by field & university.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="feature-card"><h4>Paper Summarizer</h4><p>AI summaries & simplified papers.</p></div>', unsafe_allow_html=True)

    st.subheader("For Researchers")
    c4, c5, c6 = st.columns(3)
    with c4: st.markdown('<div class="feature-card"><h4>Dataset Hub</h4><p>Curated datasets from trusted sources.</p></div>', unsafe_allow_html=True)
    with c5: st.markdown('<div class="feature-card"><h4>Pretrained Models</h4><p>Plug-and-play model suggestions.</p></div>', unsafe_allow_html=True)
    with c6: st.markdown('<div class="feature-card"><h4>Code Generator</h4><p>Get started with your code journey.</p></div>', unsafe_allow_html=True)


def render_username_page():
    st.markdown('<h1 class="landing-header">Enter your Username</h1>', unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>This will be used to save and retrieve your chat history.</div>", unsafe_allow_html=True)
    # st.write("This will be used to save and retrieve your chat history.")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username", key="username_input", placeholder="e.g., researcher123", label_visibility="collapsed")
        if st.button("Continue", use_container_width=True):
            if username:
                st.session_state.user_id = username
                st.session_state.page = "chat"
                st.session_state.messages = [{"role": "assistant", "content": f"Hi **{username}**! I'm Paperclip. How can I help you?"}]
                st.rerun()
            else:
                st.warning("Please enter a username.")

def render_chat_page():
    st.markdown(f'<h1 class="landing-header">PaperClip</h1>', unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                content = message["content"]
                code_match = re.search(r"```python\n(.*)```", content, re.DOTALL)
                if code_match:
                    pre_code_text = content.split("```python\n")[0]
                    if pre_code_text.strip(): st.markdown(pre_code_text)
                    st.code(code_match.group(1), language='python')
                else:
                    st.markdown(content)
    
    st.sidebar.success(f"Session for: **{st.session_state.user_id}**")
    if st.sidebar.button("End Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'page': del st.session_state[key]
        st.session_state.page = "landing"
        st.rerun()

    st.sidebar.subheader("Research Tools")
    commands = {"domain_discovery": "Domain Discovery", "paper_summarizer": "Paper Summarizer", "professor_finder": "Professor Finder", "dataset_hub": "Dataset Hub", "pretrained_models": "Pretrained Models", "generate_code": "Generate Code"}
    for cmd_id, cmd_label in commands.items():
        if st.sidebar.button(cmd_label, key=cmd_id, use_container_width=True):
            st.session_state.command_in_progress = cmd_id
            st.rerun()

    if st.session_state.command_in_progress:
        command = st.session_state.command_in_progress
        with st.form(key=f"{command}_form"):
            st.write(f"**Tool: {commands[command]}**")
            topic = st.text_input("Enter Topic/Query:")
            university = ""
            model_name = ""
            if command == "professor_finder":
                university = st.text_input("Enter University:")
            if command == "generate_code":
                model_name = st.text_input("Enter a Model Name (e.g., BERT):")

            if st.form_submit_button("Run Tool"):
                user_message = f"Using Tool '{commands[command]}' with topic: {topic}"
                st.session_state.messages.append({"role": "user", "content": user_message})
                assistant_response = call_api(topic, command=command, university=university, model_name=model_name)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                st.session_state.command_in_progress = None
                st.rerun()
    
    else:
        if prompt := st.chat_input("Ask Paperclip anything..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            assistant_response = call_api(prompt)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            st.rerun()

# --- MAIN ROUTER ---
load_css()
if st.session_state.page == "landing":
    render_landing_page()
elif st.session_state.page == "username":
    render_username_page()
else: # page == "chat"
    render_chat_page()