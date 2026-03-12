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
    prompt = f"""You are an expert academic tutor.
Your task is to write a clear and concise EXAM-FOCUSED explanation for the specific topic: "{module_name}".

Below is textbook content that may be relevant:
---
{context[:1800]}
---

Instructions:
1. Provide a strict definition and key points ONLY for "{module_name}".
2. Use the provided textbook content if it contains information about the topic.
3. If the textbook content does NOT contain information about this specific topic, ignore the text and provide the explanation using your own expert knowledge.
4. DO NOT explain other topics that happen to be in the text.
5. Do NOT include any extra preamble, study advice, or suggestions.
6. Just the facts, definitions, and points. Do not say "Here are the points...".
"""

    result = generate_with_phi3(prompt, temperature=0.2)
    return result.strip() if result else "Summary not available."

def _extract_granular_topics(module_name: str, module_content: str) -> list[str]:
    """
    Extracts a list of specific individual topics from a syllabus module description.
    """
    if not module_content or not module_content.strip():
        return []

    prompt = f"""You are an AI assistant helping to parse syllabus text.
Below is the text for a syllabus module named '{module_name}'.
It contains a dense list of specific topics (e.g., Waterfall Model, Agile, etc.), usually separated by commas or newlines.

Module Text:
---
{module_content}
---

Your task is to extract the specific topics from this text exactly as they appear and return them as a strict JSON array of strings. 
Do not include any numbering, bullet points, or extraneous text. 
Extract the actual individual topics mentioned in the syllabus text.
Keep them concise. Limit to a MAXIMUM of 5 topics.
Example output format:
["Waterfall Model", "Agile Methodology", "Scrum Framework"]

Return ONLY the JSON array.
"""
    result = generate_with_phi3(prompt, temperature=0.1)
    
    # Try to parse the output as JSON
    import json
    try:
        clean_result = result.replace("```json", "").replace("```", "").strip()
        topics = json.loads(clean_result)
        if isinstance(topics, list) and all(isinstance(t, str) for t in topics):
            return topics[:5]
    except:
        pass
        
    # Fallback if JSON parsing fails: split by comma or newline heuristic
    topics = [t.strip() for t in module_content.replace("\\n", ",").split(",") if t.strip()]
    return topics[:5]

# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def generate_topic_summary(topic_name: str, module_name: str, priority: str, context_text: str) -> str:
    """Generate summary string on demand using existing context."""
    return _generate_summary(f"{topic_name} ({module_name})", context_text, priority)

def analyze_topics(
    syllabus_text: str,
    pyq_text: str,
    textbook_text: str,
    chunk_embeddings: list | None = None,
    pyq_questions: list | None = None,
    pyq_embeddings: list | None = None,
    textbook_chunks: list | None = None,
    generate_summaries: bool = True,
) -> list[dict]:
    """
    Main entry point. Given raw text from all three PDFs or precomputed subsets, returns:

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

    if not syllabus_text or not syllabus_text.strip():
        # Optional: Log warning about empty syllabus
        print("⚠ Warning: Syllabus text is empty. Topic analyzer cannot proceed.")
        return []

    # ── 1. Parse inputs ──────────────────────────────────────────────────────
    modules: dict[str, str] = extract_modules_from_syllabus(syllabus_text)
    if not modules:
        return []

    if pyq_questions is None:
        pyq_questions = extract_questions_with_regex(pyq_text)
        if not pyq_questions:
            pyq_questions = [pyq_text[:2000]]

    if textbook_chunks is None:
        textbook_chunks = chunk_text(textbook_text, chunk_size=350, overlap=60)
    
    # ── 1.5 Extract granular topics ──────────────────────────────────────────
    print("🔬 Extracting specific syllabus topics from modules...")
    granular_topics = [] # list of dicts: {"module": str, "topic": str}
    
    for module_name, module_text in modules.items():
        subtopics = _extract_granular_topics(module_name, module_text)
        for st in subtopics:
            granular_topics.append({
                "module": module_name,
                "topic": st,
                "content": module_text,
            })
            
    if not granular_topics:
        return []

    # ── 2. Build embeddings ───────────────────────────────────────────────────
    print("🧠 Building embeddings for topic analysis...")
    embedding_model = get_embedding_model()

    topic_texts = [t["topic"] for t in granular_topics]

    topic_embeddings = embedding_model.embed_documents(topic_texts)
    
    if pyq_embeddings is None:
        pyq_embeddings = embedding_model.embed_documents(pyq_questions)
        
    if chunk_embeddings is None:
        chunk_embeddings = embedding_model.embed_documents(textbook_chunks)

    print(f"   → {len(topic_texts)} granular topics | {len(pyq_questions)} PYQ questions | {len(textbook_chunks)} textbook chunks")

    # ── 3. Score each topic against PYQs ─────────────────────────────────────
    raw_stats = []
    for te in topic_embeddings:
        stats = _score_module_against_pyqs(te, pyq_embeddings)
        raw_stats.append(stats)

    # ── 4. Compute a composite score for each topic ──────────────────────────
    hit_counts = [s["hit_count"] for s in raw_stats]
    avg_sims   = [s["avg_sim"]   for s in raw_stats]
    top_sims   = [s["top_sim"]   for s in raw_stats]

    norm_hits = _normalize(hit_counts)
    norm_avg  = _normalize(avg_sims)
    norm_top  = _normalize(top_sims)

    composite_scores = [
        0.50 * norm_hits[i] + 0.30 * norm_avg[i] + 0.20 * norm_top[i]
        for i in range(len(topic_texts))
    ]

    # ── 5. Classify priority and pre-sort ─────────────────────────────────────
    priorities = [_classify(s) for s in composite_scores]

    scored_topics = []
    for i, t_info in enumerate(granular_topics):
        scored_topics.append({
            "original_index": i,
            "topic": t_info["topic"],
            "module": t_info["module"],
            "priority": priorities[i],
            "score": composite_scores[i],
            "hit_count": raw_stats[i]["hit_count"],
            "avg_sim": raw_stats[i]["avg_sim"]
        })
        
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    scored_topics.sort(key=lambda x: (priority_order[x["priority"]], -x["score"]))
    
    # ── 5.5 Limit to Top 10 Topics with mixed priorities ─────────────────────
    high_topics = [t for t in scored_topics if t["priority"] == "HIGH"]
    med_topics  = [t for t in scored_topics if t["priority"] == "MEDIUM"]
    low_topics  = [t for t in scored_topics if t["priority"] == "LOW"]
    
    selected_high = high_topics[:5]
    selected_med  = med_topics[:3]
    selected_low  = low_topics[:2]
    
    rem_high = high_topics[5:]
    rem_med  = med_topics[3:]
    rem_low  = low_topics[2:]
    
    missing = 10 - (len(selected_high) + len(selected_med) + len(selected_low))
    if missing > 0:
        add_high = rem_high[:missing]
        selected_high.extend(add_high)
        missing -= len(add_high)
    if missing > 0:
        add_med = rem_med[:missing]
        selected_med.extend(add_med)
        missing -= len(add_med)
    if missing > 0:
        add_low = rem_low[:missing]
        selected_low.extend(add_low)
        missing -= len(add_low)
        
    top_10_topics = selected_high + selected_med + selected_low
    top_10_topics.sort(key=lambda x: (priority_order[x["priority"]], -x["score"]))

    # ── 6. Extract contexts and generate summaries (optional) ────────────────
    results = []
    for t_info in top_10_topics:
        topic_name = t_info["topic"]
        module_name = t_info["module"]
        priority = t_info["priority"]
        orig_i = t_info["original_index"]
        
        print(f"   → Processing: {topic_name} [{module_name}] ({priority})...")

        context_text = _find_relevant_textbook_chunks(
            topic_embeddings[orig_i],
            chunk_embeddings,
            textbook_chunks,
            top_k=4,
        )

        summary = ""
        if generate_summaries:
            summary = _generate_summary(f"{topic_name} ({module_name})", context_text, priority)

        # We keep the "module" key as it is expected by topics.html, but we set it to the topic_name.
        results.append({
            "module":    topic_name, 
            "topics":    f"Part of {module_name}",
            "priority":  priority,
            "score":     round(t_info["score"], 3),
            "hit_count": t_info["hit_count"],
            "avg_sim":   round(t_info["avg_sim"], 3),
            "context":   context_text,
            "summary":   summary,
        })

    print(f"✅ Topic analysis complete: {len(results)} distinct topics analyzed.")
    return results
