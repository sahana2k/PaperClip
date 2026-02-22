"""High-level research assistant utilities.

Generates a consolidated research bundle: ideas, paper search + summaries
with inline numeric citations and BibTeX, mind maps (Mermaid), podcast-style
scripts, code snippets, experiment design, and writing outlines.

Relies on OpenAI for generation, arXiv for papers, and GitHub for code search
when available. This is intentionally lightweight and synchronous.
"""

from typing import List, Dict, Any, Optional
import json
import re
import arxiv
from app.tools import llm, safe_invoke


def _search_arxiv(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Fetch a few arXiv papers for the topic."""
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    papers = []
    for result in search.results():
        papers.append({
            "title": result.title,
            "authors": [str(a) for a in result.authors],
            "summary": result.summary,
            "pdf_url": result.pdf_url,
            "doi": result.doi,
            "published": result.published.isoformat() if result.published else None
        })
    return papers


def _bibtex_entry(paper: Dict[str, Any], idx: int) -> str:
    key = f"paper{idx}"
    title = paper.get("title", "Untitled")
    authors = " and ".join(paper.get("authors", [])) or "Unknown"
    year = (paper.get("published", "") or "")[:4]
    doi = paper.get("doi", "") or ""
    url = paper.get("pdf_url", "") or ""
    return (
        f"@article{{{key},\n"
        f"  title={{ {title} }},\n"
        f"  author={{ {authors} }},\n"
        f"  year={{ {year} }},\n"
        f"  doi={{ {doi} }},\n"
        f"  url={{ {url} }}\n"
        f"}}"
    )


def _summarize_papers(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Produce bullet and section-wise summaries with inline citations."""
    if not papers:
        return {"bullets": "No papers found.", "comparative": "No comparative summary available.", "bibtex": []}

    # Build a prompt with enumerated papers to keep citations grounded
    paper_blocks = []
    for i, p in enumerate(papers, start=1):
        paper_blocks.append(
            f"[{i}] {p['title']} | Authors: {', '.join(p.get('authors', []))} | URL: {p.get('pdf_url','')} | Abstract: {p.get('summary','')}"
        )
    prompt = (
        "You are a precise research summarizer. Given papers with indices, write:\n"
        "1) 5 bullet takeaways with inline citations [n].\n"
        "2) Section-wise summary (Methods, Results, Limitations) using citations.\n"
        "Do NOT invent citations or papers beyond those listed.\n\n"
        "Papers:\n" + "\n".join(paper_blocks)
    )
    response = llm.invoke(prompt)
    bibtex_entries = [_bibtex_entry(p, i) for i, p in enumerate(papers, start=1)]
    return {
        "bullets": response.content,
        "comparative": "",  # kept for structure; bullets already include citations
        "bibtex": bibtex_entries,
    }


def _extract_mindmap_label(text: str) -> str:
    cleaned = re.sub(r"\[[^\]]+\]$", "", text).strip()
    double_paren = re.search(r"\(\((.+?)\)\)", cleaned)
    if double_paren:
        return double_paren.group(1).strip()

    quoted = re.search(r"\"([^\"]+)\"", cleaned)
    if quoted:
        return quoted.group(1).strip()

    paren = re.search(r"\(([^)]+)\)", cleaned)
    if paren:
        return paren.group(1).strip()

    cleaned = re.sub(r"^[a-zA-Z0-9_.-]+", "", cleaned).strip()
    return cleaned


def _sanitize_mindmap_code(topic: str, content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```mermaid"):
        stripped = stripped.replace("```mermaid", "").replace("```", "").strip()
    elif stripped.startswith("```"):
        stripped = stripped.replace("```", "").strip()

    if "\n" not in stripped and " id" in stripped:
        stripped = stripped.replace("mindmap", "mindmap\n", 1)
        stripped = re.sub(r"\s+(title:)", r"\n\1", stripped)
        stripped = re.sub(r"\s+(id\d+(?:\.\d+)?\[[^\]]+\])", r"\n\1", stripped)

    lines = [line.rstrip() for line in stripped.splitlines() if line.strip()]
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("mindmap"):
            start_idx = i
            break

    if start_idx is None:
        return "mindmap\n  root(({}))\n    overview\n    methods\n    datasets\n    evaluation".format(topic)

    cleaned = [line.replace("\t", "  ") for line in lines[start_idx:]]

    output = ["mindmap", f"  root(({topic}))"]

    for line in cleaned[1:]:
        trimmed = line.strip()
        if not trimmed or "--" in trimmed:
            continue
        if trimmed.lower().startswith("title:"):
            continue
        if trimmed.lower().startswith("root"):
            continue

        label = _extract_mindmap_label(trimmed)
        if not label:
            continue

        leading = len(line) - len(line.lstrip(" "))
        depth = 2 + max(0, (leading - 2) // 2)
        indent = "  " * depth
        output.append(f"{indent}{label}")

    return "\n".join(output)


def _generate_mind_map(topic: str, summary: str) -> str:
    prompt = (
        "Create a Mermaid mind map for the topic with key methods, subareas, and relationships."
        " Output ONLY Mermaid mindmap code. The first line must be 'mindmap'."
        " Do not wrap in markdown fences.\n"
        f"Topic: {topic}\n"
        f"Context: {summary[:1200]}"
    )
    response = llm.invoke(prompt)
    return _sanitize_mindmap_code(topic, response.content)


def _podcast_script(topic: str, bullets: str) -> str:
    prompt = (
        "Write a two-speaker podcast script (Host/Guest) explaining the research topic."
        " Include a 2-3 sentence TL;DR up front. Keep it concise (under 400 words).\n"
        f"Topic: {topic}\n"
        f"Key points: {bullets[:800]}"
    )
    return llm.invoke(prompt).content


def _code_snippet(topic: str) -> str:
    prompt = (
        "Provide a runnable Python example (PyTorch/NumPy as needed) with minimal tests/comments for the topic."
        " Keep it short and self-contained."
        f" Topic: {topic}"
    )
    return llm.invoke(prompt).content


def _experiment_plan(topic: str) -> str:
    prompt = (
        "Design an experimental plan: pipeline, datasets, metrics, and 3 ablations."
        " Provide brief rationale and common pitfalls."
        f" Topic: {topic}"
    )
    return llm.invoke(prompt).content


def _writing_outline(topic: str) -> str:
    prompt = (
        "Give a paper outline (Abstract, Intro, Related Work, Methods, Experiments, Limitations) in academic tone."
        " Use concise bullet points."
        f" Topic: {topic}"
    )
    return llm.invoke(prompt).content


def _safe_json_loads(payload: str) -> Dict[str, Any]:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {"raw": payload}


def _generate_ideation(topic: str, goal: Optional[str] = None, constraints: Optional[str] = None) -> Dict[str, Any]:
    prompt = (
        "You are a research ideation assistant. Return JSON only."
        " Create 4 research ideas. Each idea must include:"
        " title, hypothesis, novelty, feasibility, risks, next_steps."
        " Use strings for each field, and next_steps as an array of short strings."
        " Output schema: {\"ideas\": [ ... ]}. No markdown."
        f"\nTopic: {topic}\nGoal: {goal or 'N/A'}\nConstraints: {constraints or 'None'}"
    )
    response = safe_invoke(prompt)
    parsed = _safe_json_loads(response.content)
    ideas = parsed.get("ideas") if isinstance(parsed, dict) else None
    return {
        "topic": topic,
        "goal": goal,
        "constraints": constraints,
        "ideas": ideas if isinstance(ideas, list) else [],
        "raw": None if isinstance(ideas, list) else response.content,
    }


def _generate_experiment_design(topic: str, idea: Optional[str] = None, constraints: Optional[str] = None) -> Dict[str, Any]:
    prompt = (
        "You are a research experiment designer. Return JSON only."
        " Include: objective, hypothesis, datasets, metrics, baselines, methodology, ablations, compute, risks, success_criteria, timeline."
        " Use arrays for datasets, metrics, baselines, methodology, ablations, risks."
        " Output schema: {\"objective\": ..., \"hypothesis\": ..., ...}. No markdown."
        f"\nTopic: {topic}\nIdea: {idea or 'N/A'}\nConstraints: {constraints or 'None'}"
    )
    response = safe_invoke(prompt)
    parsed = _safe_json_loads(response.content)
    return {
        "topic": topic,
        "idea": idea,
        "constraints": constraints,
        "plan": parsed if isinstance(parsed, dict) else {"raw": response.content},
    }


def generate_research_bundle(topic: str) -> Dict[str, Any]:
    """Produce a composite research bundle for the topic."""
    papers = _search_arxiv(topic, max_results=3)
    paper_summaries = _summarize_papers(papers)

    # Use the bullet summary to ground other generations
    bullets = paper_summaries.get("bullets", "")

    bundle = {
        "topic": topic,
        "papers": papers,
        "summaries": paper_summaries,
        "mind_map": _generate_mind_map(topic, bullets),
        "podcast_script": _podcast_script(topic, bullets),
        "code_snippet": _code_snippet(topic),
        "experiment_plan": _experiment_plan(topic),
        "writing_outline": _writing_outline(topic),
    }
    return bundle
