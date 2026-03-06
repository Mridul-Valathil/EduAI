

# from generation.phi3_wrapper import generate_with_phi3


# def generate_mcqs(topic, context):

#     prompt = f"""
# You are a strict university exam paper setter.

# Generate EXACTLY 5 multiple choice questions
# STRICTLY about: {topic}

# Use ONLY the content provided below.
# Do NOT add external knowledge.

# Content:
# {context}

# Return ONLY valid JSON.
# No extra commentary.
# No markdown.
# No emojis.
# No symbols.

# Format EXACTLY like this:

# [
#   {{
#     "question": "Question text",
#     "option_A": "Option A text",
#     "option_B": "Option B text",
#     "option_C": "Option C text",
#     "option_D": "Option D text",
#     "answer": "A",
#     "explanation": "Short explanation"
#   }}
# ]
# """

#     return generate_with_phi3(prompt)


# from generation.phi3_wrapper import generate_with_phi3


# def generate_mcqs(topic, context):

#     prompt = f"""
# You are a strict university exam generator.

# Generate EXACTLY 5 multiple choice questions.

# STRICT RULES:
# - Each question must have EXACTLY 4 options.
# - Options must be labeled ONLY as A, B, C, D.
# - There must be ONLY ONE correct answer.
# - The answer field must contain ONLY one letter: A or B or C or D.
# - Do NOT generate multiple answers.
# - Do NOT write phrases like "A and B".
# - Do NOT add markdown.
# - Do NOT add ```json.
# - Output must start with [ and end with ].
# - Output must be valid JSON only.

# Content:
# {context}

# Format:

# [
#   {{
#     "question": "...",
#     "option_A": "...",
#     "option_B": "...",
#     "option_C": "...",
#     "option_D": "...",
#     "answer": "A",
#     "explanation": "..."
#   }}
# ]
# """

#     return generate_with_phi3(prompt)








# from generation.phi3_wrapper import generate_with_phi3


# def generate_single_mcq(context):
#     prompt = f"""
# Generate ONE multiple choice question.

# STRICT RULES:
# - Exactly 4 options.
# - Options must be labeled A, B, C, D.
# - Only ONE correct answer.
# - Answer must be exactly A or B or C or D.
# - Return ONLY valid JSON.
# - Do NOT include markdown.
# - Do NOT include extra text.

# Format:

# {{
#   "question": "...",
#   "option_A": "...",
#   "option_B": "...",
#   "option_C": "...",
#   "option_D": "...",
#   "answer": "A",
#   "explanation": "..."
# }}

# Content:
# {context}
# """
#     return generate_with_phi3(prompt)







from generation.phi3_wrapper import generate_with_phi3


def generate_single_mcq(context, difficulty="Medium"):
    prompt = f"""
Generate ONE multiple choice question.

Difficulty Level: {difficulty.upper()}
Note on difficulty:
- EASY: Direct recall, simple definitions.
- MEDIUM: Application of concepts, simple comparisons.
- HARD: Deep analysis, complex scenarios, multi-step reasoning.

STRICT RULES:
- Exactly 4 options.
- Options must be labeled A, B, C, D.
- Only ONE correct answer.
- Answer must be exactly A or B or C or D.
- Return ONLY valid JSON.
- Do NOT include markdown.
- Do NOT include extra text.
- Do NOT wrap in ```json.

Format:

{{
  "question": "Question text here [{difficulty}]",
  "option_A": "Option text",
  "option_B": "Option text",
  "option_C": "Option text",
  "option_D": "Option text",
  "answer": "A",
  "explanation": "Short explanation here"
}}

Content:
{context}
"""
    return generate_with_phi3(prompt)