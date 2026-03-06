from preprocessing.pdf_extractor import extract_text_from_pdf
from preprocessing.chunker import chunk_text
from generation.phi3_wrapper import generate_with_phi3

import re
import json

def extract_questions_with_regex(pyq_text):
    """
    Splits PYQ text using common question-start verbs.
    Fast, but brittle to different PDF formats.
    """
    text = re.sub(r'\s+', ' ', pyq_text)
    text = re.sub(r'\(\d+\)', '', text)
    text = text.replace(" OR ", " ")
    text = re.sub(r'Page \d+ of \d+', ' ', text)
    text = re.sub(r'Module\s+[IVX]+', ' ', text)
    text = re.sub(r'\*+', ' ', text)
    text = re.sub(r'\b\d{10,}\b', ' ', text)
    text = re.sub(r'PART\s+[A-Z].*?(?=(?:\d+[\.\)]?\s*)?(?:What|Explain|Define|Write|Discuss|Illustrate|With|How|Why))', ' ', text)

    verbs = ["What", "Explain", "Define", "Write", "Discuss", "Illustrate", "Tllustrate", "With", "How", "Why"]
    pattern = r'(?=\b(?:\d+[\.\)]?\s*)?(?:' + "|".join(verbs) + r')\b)'
    splits = re.split(pattern, text)

    questions = []
    for q in splits:
        q = q.strip()
        q_cleaned = re.sub(r'^\d+[\.\)]?\s*', '', q)
        q_cleaned = re.sub(r'\s+\d+\s*marks\.', '', q_cleaned)

        if len(q_cleaned) > 10 and any(q_cleaned.startswith(v) for v in verbs):
            questions.append(q_cleaned)

    return questions


def extract_questions_with_llm(pyq_text):
    """
    Universal slow-but-smart parser using Phi-3 to semantically 
    extract questions regardless of PDF formatting.
    """
    prompt_template = """
You are an advanced academic text parser. I am providing you with a chunk of unstructured text from an exam paper.
Your ONLY task is to identify every question in this chunk and extract its text verbatim.

STRICT RULES:
1. ONLY return a JSON list of strings. Each string is the text of a single question.
2. The exam may contain multiple-choice questions, short-answer questions, and long-answer questions. Extract the text for ALL of them.
3. For multiple-choice questions, EXTRACT the question text, but DO NOT include the options (A, B, C, D) in your extraction.
4. Do not include question numbers (e.g. "1.", "Q2") in the extracted strings.
5. Do not include exam instructions, section headers (e.g. "SECTION A"), or marks (e.g. "[5 marks]").
6. If a question spans multiple lines, combine it into one single string.
7. Return ONLY the JSON formatting. Do not wrap in markdown or add conversational text.
8. IF THERE ARE NO QUESTIONS IN THIS CHUNK, return an empty array [].

Text Chunk:
-------------
{chunk}
-------------

JSON Output:
"""
    
    chunks = chunk_text(pyq_text)
    print(f"📄 Processing paper in {len(chunks)} chunks with Phi-3 (may take a minute)...")
    
    all_questions = []
    
    for i, chunk in enumerate(chunks):
        print(f"   -> Scanning chunk {i+1}/{len(chunks)}...")
        prompt = prompt_template.replace("{chunk}", chunk)
        raw_output = generate_with_phi3(prompt)
        cleaned = raw_output.replace("```json", "").replace("```", "").strip()
        
        try:
            questions = json.loads(cleaned)
            if isinstance(questions, list):
                all_questions.extend(questions)
        except Exception:
            pass  # gracefully ignore hallucinatory chunks

    return all_questions


def extract_pyq_text(pyq_pdf_path):
    return extract_text_from_pdf(pyq_pdf_path)


# -------------------------------------------------------------
# NEW: Extract Paper Pattern (Section Structure)
# -------------------------------------------------------------

def extract_paper_pattern(pyq_text):
    """
    Extracts exam structure such as:
    PART A (10 x 1 = 10)
    PART B (5 x 4 = 20)
    PART C (3 x 10 = 30)

    Returns:
    {
        "PART A": {"count": 10, "marks": 1},
        "PART B": {"count": 5, "marks": 4},
        ...
    }
    """

    pattern_dict = {}

    text = re.sub(r'\s+', ' ', pyq_text)

    # Match patterns like: PART A (10 x 1 = 10)
    matches = re.findall(
        r'(PART\s+[A-Z])\s*\(\s*(\d+)\s*[xX]\s*(\d+)',
        text,
        re.IGNORECASE
    )

    for match in matches:
        section = match[0].upper()
        count = int(match[1])
        marks = int(match[2])

        pattern_dict[section] = {
            "count": count,
            "marks": marks
        }

    return pattern_dict


# -------------------------------------------------------------
# NEW: Extract Style Profile From PYQ Questions
# -------------------------------------------------------------

def extract_style_profile(pyq_questions):
    """
    Analyzes question style:
    - Average length
    - Common command verbs
    - Distribution of question types

    Returns:
    {
        "avg_length": float,
        "common_verbs": [...],
        "type_distribution": {...}
    }
    """

    if not pyq_questions:
        return {}

    verbs = ["What", "Explain", "Define", "Write", "Discuss",
             "Illustrate", "How", "Why", "Compare", "Differentiate"]

    verb_counts = {}
    type_distribution = {
        "definition": 0,
        "explanation": 0,
        "application": 0
    }

    total_length = 0

    for q in pyq_questions:
        words = q.split()
        total_length += len(words)

        # Detect verb usage
        for verb in verbs:
            if q.startswith(verb):
                verb_counts[verb] = verb_counts.get(verb, 0) + 1

                if verb in ["Define", "What"]:
                    type_distribution["definition"] += 1
                elif verb in ["Explain", "Discuss", "Illustrate"]:
                    type_distribution["explanation"] += 1
                elif verb in ["How", "Why", "Compare", "Differentiate"]:
                    type_distribution["application"] += 1
                break

    avg_length = total_length / len(pyq_questions)

    # Sort verbs by frequency
    sorted_verbs = sorted(
        verb_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    common_verbs = [v[0] for v in sorted_verbs[:5]]

    # Normalize distribution
    total_classified = sum(type_distribution.values())
    if total_classified > 0:
        for k in type_distribution:
            type_distribution[k] = round(
                type_distribution[k] / total_classified,
                2
            )

    return {
        "avg_length": round(avg_length, 2),
        "common_verbs": common_verbs,
        "type_distribution": type_distribution
    }