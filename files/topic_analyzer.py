"""
topic_analyzer.py
-----------------
Analyzes syllabus modules against PYQ questions to:
  1. Score each topic HIGH / MEDIUM / LOW priority
  2. Generate a concise summary for each topic

This module is self-contained and plugs into web_app.py via a single call:
    results = analyze_topics(syllabus_text, pyq_text, textbook_text)
"""

import numpy as np
from preprocessing.pdf_extractor import extract_text_from_pdf
from preprocessing.chunker import chunk_text
from pyq_engine.pyq_parser import extract_questions_with_regex
from syllabus_engine.syllabus_parser import extract_modules_from_syllabus
from vector_db.embedding_model import get_embedding_model
from generation.phi3_wrapper import generate_with_phi3


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _cosine_similarity(a: list, b: list) -> float:
    """Safe cosine similarity between two vectors."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def _score_module_against_pyqs(
    module_embedding: list,
    pyq_embeddings: list,
    threshold: float = 0.45,
) -> dict:
    """
    For a single module, compute:
      - hit_count   : number of PYQ questions with similarity > threshold
      - avg_sim     : average similarity across all PYQ questions
      - top_sim     : highest single similarity score
    """
    similarities = [_cosine_similarity(module_embedding, qe) for qe in pyq_embeddings]
    hits = [s for s in similarities if s >= threshold]

    return {
        "hit_count": len(hits),
        "avg_sim": float(np.mean(similarities)) if similarities else 0.0,
        "top_sim": float(max(similarities)) if similarities else 0.0,
    }


def _normalize(values: list) -> list:
    """Min-max normalize a list of floats to [0, 1]."""
    mn, mx = min(values), max(values)
    if mx == mn:
        return [0.5] * len(values)
    return [(v - mn) / (mx - mn) for v in values]


def _classify(score: float) -> str:
    """Map a normalized score to a priority label."""
    if score >= 0.60:
        return "HIGH"
    elif score >= 0.30:
        return "MEDIUM"
    else:
        return "LOW"


def _find_relevant_textbook_chunks(
    module_embedding: list,
    chunk_embeddings: list,
    chunks: list,
    top_k: int = 4,
    threshold: float = 0.40,
) -> str:
    """
    Return a string of the top-k textbook chunks most relevant to this module.
    Used as context for summary generation.
    """
    scored = [
        (i, _cosine_similarity(module_embedding, ce))
        for i, ce in enumerate(chunk_embeddings)
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    relevant = [
        chunks[i] for i, sim in scored[:top_k] if sim >= threshold
    ]

    if not relevant:
        # Fall back to top-1 even if below threshold
        relevant = [chunks[scored[0][0]]]

    return "\n\n".join(relevant)


def _generate_summary(module_name: str, context: str, priority: str) -> str:
    """
    Ask the LLM to write a concise topic summary from textbook context.
    The priority label is passed in so the prompt can emphasize exam relevance.
    """
    importance_note = {
        "HIGH": "This is a HIGH priority topic that appears frequently in previous year exams.",
        "MEDIUM": "This is a MEDIUM priority topic that appears occasionally in exams.",
        "LOW": "This is a LOW priority topic with rare exam appearances.",
    }.get(priority, "")

    prompt = f"""You are an expert academic tutor writing a study guide.

Topic: {module_name}
{importance_note}

Below is relevant textbook content for this topic:
---
{context[:1800]}
---

Write a clear and concise summary of this topic in 4-6 sentences.
Focus on the key concepts, definitions, and ideas a student must know.
Do NOT copy text word-for-word. Write in your own words.
Do NOT include bullet points or headers. Write as a single paragraph.
Start directly with the content — no preamble like "This topic covers..." or "In this module...".
"""

    result = generate_with_phi3(prompt, temperature=0.3)
    return result.strip() if result else "Summary not available."


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def analyze_topics(
    syllabus_text: str,
    pyq_text: str,
    textbook_text: str,
    generate_summaries: bool = True,
) -> list[dict]:
    """
    Main entry point. Given raw text from all three PDFs, returns:

    [
      {
        "module": "Module 1 [8 hrs]",
        "topics": "Introduction to ...",   # raw syllabus content
        "priority": "HIGH" | "MEDIUM" | "LOW",
        "score": 0.87,                     # normalized 0–1
        "hit_count": 5,                    # number of matching PYQ questions
        "summary": "This module covers...", # generated by LLM
      },
      ...
    ]

    Set generate_summaries=False to skip LLM calls (faster, no summaries).
    """

    # ── 1. Parse inputs ──────────────────────────────────────────────────────
    modules: dict[str, str] = extract_modules_from_syllabus(syllabus_text)
    if not modules:
        return []

    pyq_questions: list[str] = extract_questions_with_regex(pyq_text)
    if not pyq_questions:
        # If no PYQs extracted, fall back to treating full pyq_text as one question
        pyq_questions = [pyq_text[:2000]]

    textbook_chunks: list[str] = chunk_text(textbook_text, chunk_size=350, overlap=60)

    # ── 2. Build embeddings ───────────────────────────────────────────────────
    print("🧠 Building embeddings for topic analysis...")
    embedding_model = get_embedding_model()

    module_names = list(modules.keys())
    module_texts = list(modules.values())

    module_embeddings = embedding_model.embed_documents(module_texts)
    pyq_embeddings = embedding_model.embed_documents(pyq_questions)
    chunk_embeddings = embedding_model.embed_documents(textbook_chunks)

    print(f"   → {len(module_names)} modules | {len(pyq_questions)} PYQ questions | {len(textbook_chunks)} textbook chunks")

    # ── 3. Score each module against PYQs ─────────────────────────────────────
    raw_stats = []
    for me in module_embeddings:
        stats = _score_module_against_pyqs(me, pyq_embeddings)
        raw_stats.append(stats)

    # ── 4. Compute a composite score for each module ──────────────────────────
    # Weighted combination: 50% hit_count, 30% avg_sim, 20% top_sim
    hit_counts = [s["hit_count"] for s in raw_stats]
    avg_sims   = [s["avg_sim"]   for s in raw_stats]
    top_sims   = [s["top_sim"]   for s in raw_stats]

    norm_hits = _normalize(hit_counts)
    norm_avg  = _normalize(avg_sims)
    norm_top  = _normalize(top_sims)

    composite_scores = [
        0.50 * norm_hits[i] + 0.30 * norm_avg[i] + 0.20 * norm_top[i]
        for i in range(len(module_names))
    ]

    # ── 5. Classify priority ──────────────────────────────────────────────────
    priorities = [_classify(s) for s in composite_scores]

    # ── 6. Generate summaries (optional) ─────────────────────────────────────
    results = []
    for i, name in enumerate(module_names):
        print(f"   → Processing: {name} ({priorities[i]})...")

        summary = ""
        if generate_summaries:
            context_text = _find_relevant_textbook_chunks(
                module_embeddings[i],
                chunk_embeddings,
                textbook_chunks,
                top_k=4,
            )
            summary = _generate_summary(name, context_text, priorities[i])

        results.append({
            "module":    name,
            "topics":    modules[name],
            "priority":  priorities[i],
            "score":     round(composite_scores[i], 3),
            "hit_count": raw_stats[i]["hit_count"],
            "avg_sim":   round(raw_stats[i]["avg_sim"], 3),
            "summary":   summary,
        })

    # ── 7. Sort: HIGH first, then MEDIUM, then LOW; within each group by score ─
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    results.sort(key=lambda x: (priority_order[x["priority"]], -x["score"]))

    print(f"✅ Topic analysis complete: {len(results)} modules analyzed.")
    return results
