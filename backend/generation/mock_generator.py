from generation.phi3_wrapper import generate_with_phi3


def generate_mock_paper(pyq_text, textbook_chunks):
    """
    Simple mock generator:
    - Uses PYQ to understand format
    - Uses textbook for content
    - Generates entire paper in ONE call
    """

    # Use small portion of textbook for context
    context = "\n\n".join(textbook_chunks[:10])
    context = context[:3000]  # limit size slightly higher since we want more content

    prompt = f"""
Generate a mock examination paper based ONLY on the provided TEXTBOOK CONTENT.

STRICT FORMATTING RULES:
1. You must output exactly two sections: "PART A" and "PART B".
2. Under PART A, list EXACTLY 10 short-answer questions numbered 1 to 10.
3. Under PART B, list EXACTLY 10 longer questions numbered 11 to 20. You may use "OR" between choices.
4. STOP GENERATING after question 20. DO NOT generate more than 20 questions in total.
5. DO NOT output any other headings (no "Module", no "University", etc.).
6. DO NOT output ANY conversational text, preambles, or explanations.
7. ONLY output the questions.
8. ALL questions must be derived from the TEXTBOOK CONTENT. Do not use external knowledge.

--- TEXTBOOK CONTENT ---
{context}
------------------------

EXAMPLE OF THE EXACT EXPECTED OUTPUT FORMAT:
PART A
1. [Question based on textbook content]
2. [Question based on textbook content]
...
10. [Question based on textbook content]

PART B
11. [Longer question based on textbook content]
OR
12. [Alternative longer question based on textbook content]
...
20. [Last longer question based on textbook content]

OUTPUT THE EXAM PAPER NOW, STARTING WITH "PART A":
"""

    return generate_with_phi3(prompt, max_tokens=1500).strip()