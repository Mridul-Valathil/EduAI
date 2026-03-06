# from generation.phi3_wrapper import generate_with_phi3


# def generate_mock_paper(pyq_text, textbook_chunks):
#     """
#     Simple mock generator:
#     - Uses PYQ to understand format
#     - Uses textbook for content
#     - Generates entire paper in ONE call
#     """

#     # Use small portion of textbook for context
#     context = "\n\n".join(textbook_chunks[:5])
#     context = context[:1500]  # limit size

#     # Use only question section from PYQ (first 1500 chars)
#     pyq_sample = pyq_text[:1500]

#     prompt = f"""
# You are generating a university mock examination paper.

# Use the following Previous Year Question (PYQ) format as reference:
# # 
# --------------------
# {pyq_sample}
# --------------------

# Now generate a NEW mock question paper:

# Requirements:
# - Follow EXACT same structure as PYQ
# - Include only:
#     PART A
#     PART B
# - Same numbering style
# - Same module structure
# - Same use of "OR"
# - Only questions
# - No university header
# - No marks brackets
# - No explanations
# - Plain text only

# Generate questions strictly from the textbook content below:

# --------------------
# {context}
# --------------------

# Return full mock paper.
# """

#     return generate_with_phi3(prompt).strip()

from generation.phi3_wrapper import generate_with_phi3


def generate_mock_paper(pyq_text, textbook_chunks):

    # Use very small context for speed
    context = textbook_chunks[0][:800]
    pyq_sample = pyq_text[:800] if pyq_text else "No PYQ provided."

    prompt = f"""
Generate a university mock examination paper.

Below is a sample from the Previous Year Question (PYQ) to show you the REQUIRED FORMAT and structure:
---
{pyq_sample}
---

STRICT RULES:
- IMPORTANT: You MUST output questions in the EXACT SAME formatting, numbering style, sections, and "OR" choices layout as the PYQ sample above.
- Ensure 'Part A' questions are marked as 3 marks questions.
- Ensure 'Part B' questions are appropriately numbered.
- The generated questions MUST be highly accurate and directly drawn from the textbook context below. Do not hallucinate topics outside this context.
- Only output the paper text.
- No explanations or filler.
- Plain text only.

Generate questions strictly from this content:
---
{context}
---
"""

    return generate_with_phi3(prompt).strip()