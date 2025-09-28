# app/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

# NOTE: We no longer need lifespan or async SQLAlchemy imports
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.tools import all_tools, llm
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# --- INITIALIZATION (lifespan is no longer needed) ---
app = FastAPI(
    title="Paperclip API",
    version="5.0.0",
    servers=[{"url": "http://127.0.0.1:8000", "description": "Local Development Server"}]
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    user_id: str
    query: str
    command: Optional[str] = None
    university: Optional[str] = None
    model_name: Optional[str] = None

# --- AGENT & MEMORY SETUP ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Paperclip, a helpful research assistant."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
agent = create_tool_calling_agent(llm, list(all_tools.values()), prompt)
agent_executor = AgentExecutor(agent=agent, tools=list(all_tools.values()), verbose=True)

def get_session_history(session_id: str) -> SQLChatMessageHistory:
    db_path = f"./{session_id}.db"
    # --- CHANGE: Use the standard synchronous connection string ---
    return SQLChatMessageHistory(session_id=session_id, connection_string=f"sqlite:///{db_path}")

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# --- API ENDPOINT (NOW SYNCHRONOUS) ---
@app.post("/query")
def handle_query(request: QueryRequest): # <-- REMOVED 'async'
    """Handles all user queries with automatic, persistent session history."""
    
    if request.command and request.command in all_tools:
        # Tool calls can remain synchronous
        tool_to_run = all_tools[request.command]
        tool_args = {}
        if request.command in ["domain_discovery", "paper_summarizer", "dataset_hub", "pretrained_models"]:
            tool_args['topic'] = request.query
        elif request.command == "professor_finder":
            tool_args['topic'] = request.query
            tool_args['university'] = request.university
        elif request.command == "generate_code":
            tool_args['topic'] = request.query
            tool_args['model_name'] = request.model_name
        
        if any(v is None for v in tool_args.values()):
             raise HTTPException(status_code=400, detail=f"Missing required arguments for the tool: {request.command}")

        try:
            response_text = tool_to_run.invoke(tool_args)
            return {"response": response_text}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Conversational chat with memory
        config = {"configurable": {"session_id": request.user_id}}
        # --- CHANGE: Use the synchronous 'invoke' instead of 'ainvoke' ---
        response = agent_with_chat_history.invoke({"input": request.query}, config=config)
        return {"response": response["output"]}

@app.get("/")
def read_root():
    return {"status": "Paperclip API is running with local DB memory."}