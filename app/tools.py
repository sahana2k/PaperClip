# app/tools.py
import os
import re
import arxiv
from github import Github, Auth
from huggingface_hub import HfApi, hf_hub_download
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from semanticscholar import SemanticScholar
from langchain_cohere import ChatCohere
# --- INITIALIZATION ---
# Use Gemini for all tool-internal LLM tasks
llm = ChatCohere(
    model="command-a-03-2025",
    temperature=0,
    cohere_api_key="cohere_api_key"
)
s2 = SemanticScholar()
hf_api = HfApi()

# Check for and initialize the GitHub client
github_token = "GITHUB_TOKEN-"
if not github_token:
    raise ValueError(
        "GITHUB_TOKEN not found in environment variables. "
        "Please ensure it is set in your .env file."
    )
github_auth = Auth.Token(github_token)
g = Github(auth=github_auth)

# --- DYNAMIC TOOLS ---

@tool
def domain_discovery_tool(topic: str) -> str:
    """Finds and suggests specific subfields for a broad research topic."""
    prompt = f"What are the key subfields and emerging areas within the research domain of '{topic}'? Provide a concise list of 3-4 options."
    response = llm.invoke(prompt)
    return response.content

@tool
def paper_summarizer_tool(query: str) -> str:
    """Searches for and summarizes recent research papers from ArXiv based on a query."""
    # This tool's code remains the same as before
    search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
    # ... (rest of the logic is identical to the previous version)
    results = list(search.results())
    if not results: return "No papers found."
    summaries = [f"Title: {r.title}\nURL: {r.pdf_url}\nSummary: {llm.invoke(f'Summarize this abstract in 3 sentences: {r.summary}').content}\n---" for r in results]
    return "\n".join(summaries)


@tool
def professor_finder_tool(topic: str, university: str) -> str:
    """
    Finds professors at a specific university working on a given topic
    by first finding relevant papers and then checking the authors' affiliations.
    """
    try:
        # Step 1: Search for papers related to the topic.
        papers = s2.search_paper(topic, limit=20)
        
        found_professors = {} # Use a dict to store unique professors by their ID

        # Step 2: Iterate through the papers and their authors.
        for paper in papers:
            for author in paper.authors:
                # Step 3: Check if the author has affiliations listed.
                if author.affiliations:
                    # Step 4: Check if any affiliation matches the target university.
                    if any(university.lower() in aff.lower() for aff in author.affiliations):
                        # Add the professor to our dictionary to avoid duplicates.
                        if author.authorId and author.authorId not in found_professors:
                            # Fetch more details to get a homepage URL if available
                            detailed_author = s2.get_author(author.authorId)
                            found_professors[author.authorId] = {
                                "name": detailed_author.name,
                                "affiliation": detailed_author.affiliations[0] if detailed_author.affiliations else "N/A",
                                "homepage": detailed_author.url,
                                "paper_count": detailed_author.paperCount,
                                "h_index": detailed_author.hIndex
                            }
            
            # Stop once we have a few good results.
            if len(found_professors) >= 3:
                break
        
        if not found_professors:
            return f"Could not find any professors at {university} who have recently published on '{topic}'."

        # Step 5: Format the results for display.
        response_lines = ["Found these actively publishing researchers:\n"]
        for prof in found_professors.values():
            response_lines.append(
                f"**Name:** {prof['name']} (h-index: {prof['h_index']})\n"
                f"**Affiliation:** {prof['affiliation']}\n"
                f"**Homepage:** {prof['homepage']}\n---"
            )
        
        return "\n".join(response_lines)

    except Exception as e:
        return f"An error occurred while searching for professors: {e}"

@tool
def dataset_hub_tool(topic: str) -> str:
    """
    Finds relevant datasets for a given topic, leveraging Cohere's knowledge and web search.
    """
    prompt = f"Find and describe 3 relevant, publicly available datasets for the research topic: '{topic}'. Include links to where they can be found. Prioritize datasets commonly used in academic research."
    response = llm.invoke(prompt)
    return response.content

@tool
def pretrained_model_tool(topic: str) -> str:
    """
    Finds pretrained models for a given topic from web, Cohere, and GitHub sources.
    """
    prompt = f"Search the web to find 3 popular pretrained models for '{topic}'. For each, provide its name, a brief description, and a link to its source (e.g., GitHub, Hugging Face, TensorFlow Hub)."
    response = llm.invoke(prompt)
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
    code = llm.invoke(prompt).content
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