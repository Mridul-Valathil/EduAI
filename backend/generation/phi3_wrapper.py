
# import subprocess


# def generate_with_phi3(prompt):
#     process = subprocess.run(
#         ["ollama", "run", "phi3"],
#         input=prompt,
#         capture_output=True,
#         text=True
#     )

#     return process.stdout.strip()

import ollama


def generate_with_phi3(prompt, temperature=0.1):
    """
    Generates text using Phi-3 Mini via Ollama Python API.

    Args:
        prompt (str): The input prompt.
        temperature (float): Controls randomness (default 0.1 for stable JSON).

    Returns:
        str: Generated response text.
    """

    try:
        response = ollama.chat(
            model="phi3:mini",   # 🔥 Explicitly lock model version
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": 512   # limit generation length
            }
        )

        return response["message"]["content"].strip()

    except Exception as e:
        print("⚠ Phi-3 generation error:", e)
        return ""