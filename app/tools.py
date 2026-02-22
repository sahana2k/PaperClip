# app/tools.py
import os
import re
import arxiv
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Optional
from github import Github, Auth
from huggingface_hub import HfApi, hf_hub_download
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from app.core import settings, get_logger
from app.core.exceptions import ConfigurationError

logger = get_logger(__name__)

DEFAULT_LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", "25"))


def safe_invoke(prompt: str, timeout_seconds: Optional[int] = None):
    timeout = timeout_seconds or DEFAULT_LLM_TIMEOUT
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(llm.invoke, prompt)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError as exc:
            future.cancel()
            raise TimeoutError(f"LLM request exceeded {timeout} seconds") from exc
        except Exception as exc:
            if exc.__class__.__name__ in {"ReadTimeout", "TimeoutException"}:
                raise TimeoutError("LLM provider read timeout") from exc
            raise

# --- INITIALIZATION ---
try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=512,
        timeout=10.0,
        groq_api_key=settings.groq_api_key
    )
    logger.info("✅ Groq LLM initialized (llama-3.3-70b-versatile)")
except Exception as e:
    logger.error(f"Failed to initialize Groq: {e}")
    raise ConfigurationError("Groq API configuration failed")

hf_api = HfApi()

# Check for and initialize the GitHub client (optional)
g = None
if settings.github_token:
    try:
        github_auth = Auth.Token(settings.github_token)
        g = Github(auth=github_auth)
        logger.info("✅ GitHub client initialized")
    except Exception as e:
        logger.warning(f"GitHub client not initialized (continuing without GitHub): {e}")
else:
    logger.warning("GitHub token not set; code search features will be limited.")

# --- DYNAMIC TOOLS ---

@tool
def domain_discovery_tool(topic: str) -> str:
    """Finds and suggests specific subfields for a broad research topic."""
    prompt = f"What are the key subfields and emerging areas within the research domain of '{topic}'? Provide a concise list of 3-4 options."
    response = safe_invoke(prompt)
    return response.content

@tool
def paper_summarizer_tool(topic: str) -> str:
    """Searches for and summarizes recent research papers from ArXiv based on a topic."""
    query = topic
    search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
    results = list(search.results())
    if not results:
        return "No papers found."
    paper_blocks = []
    for idx, r in enumerate(results, start=1):
        paper_blocks.append(
            f"[{idx}] Title: {r.title}\nURL: {r.pdf_url}\nAbstract: {r.summary}"
        )
    prompt = (
        "Summarize each paper in 2-3 sentences."
        " Use the exact format:\n"
        "Title: <title>\nURL: <url>\nSummary: <summary>\n---\n"
        "Do not add extra commentary.\n\n"
        "Papers:\n" + "\n\n".join(paper_blocks)
    )
    try:
        response = safe_invoke(prompt).content
    except TimeoutError as exc:
        return f"Timed out while summarizing papers: {exc}"
    return response


@tool
def professor_finder_tool(topic: str, university: str) -> str:
    """
    Finds professors at a specific university working on a given topic
    by first finding relevant papers and then checking the authors' affiliations.
    """
    try:
        # Fallback heuristic without Semantic Scholar: generate guided search queries
        prompt = (
            "List 3-5 professors at the university working on the topic. Provide name, department, homepage (if known),"
            " and a recent paper title. Prefer official lab/edu pages; avoid fabrication."
            f" Topic: {topic}\nUniversity: {university}"
        )
        return safe_invoke(prompt).content
    except Exception as e:
        return f"An error occurred while searching for professors: {e}"

@tool
def dataset_hub_tool(topic: str) -> str:
    """
    Finds relevant datasets for a given topic, leveraging Cohere's knowledge and web search.
    """
    prompt = f"Find and describe 3 relevant, publicly available datasets for the research topic: '{topic}'. Include links to where they can be found. Prioritize datasets commonly used in academic research."
    response = safe_invoke(prompt)
    return response.content

@tool
def pretrained_model_tool(topic: str) -> str:
    """
    Finds pretrained models for a given topic from web, Cohere, and GitHub sources.
    """
    prompt = f"Search the web to find 3 popular pretrained models for '{topic}'. For each, provide its name, a brief description, and a link to its source (e.g., GitHub, Hugging Face, TensorFlow Hub)."
    response = safe_invoke(prompt)
    return response.content

@tool
def generate_code_tool(topic: str, model_name: str) -> str:
    """Generates a boilerplate Colab notebook for a given topic and model name."""
    prompt = f"""Generate a Python script for a Google Colab notebook.
    The goal is to provide a starter for a project on '{topic}' using a model like '{model_name}'.
    The script must include:
    1. Pip installs for common libraries (e.g., transformers, torch, scikit-learn).
    2. Example code to load a relevant sample dataset.
    3. Example code to load a pretrained model similar to '{model_name}'.
    4. A simple inference or processing example with comments.
    """
    code = safe_invoke(prompt).content
    return f"Here is a starter Colab notebook for your project on {topic}:\n\n{code}"


# This list is for reference; we will call tools directly in the new flow.
all_tools = {
    "domain_discovery": domain_discovery_tool,
    "paper_summarizer": paper_summarizer_tool,
    "professor_finder": professor_finder_tool,
    "dataset_hub": dataset_hub_tool,
    "pretrained_models": pretrained_model_tool,
    "generate_code": generate_code_tool,
}