# from preprocessing.pdf_extractor import extract_text_from_pdf
# from preprocessing.chunker import chunk_text
# from vector_db.embedding_model import get_embedding_model
# from vector_db.vector_store import create_vector_store
# from vector_db.retriever import retrieve_chunks
# from generation.mcq_generator import generate_mcqs


# def main():
#     print("🚀 Program started")

#     # IMPORTANT: Place textbook.pdf inside backend folder
#     pdf_path = "textbook.pdf"

#     try:
#         print("📘 Extracting text...")
#         text = extract_text_from_pdf(pdf_path)
#         print("✅ Extraction complete")
#         print("Text length:", len(text))

#         if len(text) == 0:
#             print("⚠ PDF extraction returned empty text.")
#             return

#     except Exception as e:
#         print("❌ Error during PDF extraction:", e)
#         return

#     try:
#         print("✂ Chunking text...")
#         chunks = chunk_text(text)
#         print(f"✅ Total chunks created: {len(chunks)}")

#     except Exception as e:
#         print("❌ Error during chunking:", e)
#         return

#     try:
#         print("🧠 Creating embeddings...")
#         embedding_model = get_embedding_model()
#         vector_store = create_vector_store(chunks, embedding_model)
#         print("✅ Embeddings stored successfully")

#     except Exception as e:
#         print("❌ Error during embedding/vector store creation:", e)
#         return

#     topic = input("\nEnter topic for MCQ generation: ")

#     try:
#         print("🔎 Retrieving relevant content...")
#         retrieved_chunks = retrieve_chunks(vector_store, topic)

#         if not retrieved_chunks:
#             print("⚠ No relevant chunks found.")
#             return

#         context = "\n\n".join(retrieved_chunks)

#     except Exception as e:
#         print("❌ Error during retrieval:", e)
#         return

#     try:
#         print("🤖 Generating MCQs using Phi-3...\n")
#         mcqs = generate_mcqs(topic, context)
#         print("\n================ GENERATED MCQs ================\n")
#         print(mcqs)

#     except Exception as e:
#         print("❌ Error during MCQ generation:", e)
#         return


# if __name__ == "__main__":
#     main()






# import random
# import json
# from gamification.quiz_engine import run_quiz

# from preprocessing.pdf_extractor import extract_text_from_pdf
# from preprocessing.chunker import chunk_text
# from vector_db.embedding_model import get_embedding_model
# from vector_db.vector_store import create_vector_store
# from generation.mcq_generator import generate_mcqs


# def clean_llm_output(output: str) -> str:
#     """
#     Removes markdown wrappers and trims whitespace.
#     """
#     return (
#         output.replace("```json", "")
#         .replace("```", "")
#         .strip()
#     )

# def is_valid_schema(mcqs):
#     required_keys = {
#         "question",
#         "option_A",
#         "option_B",
#         "option_C",
#         "option_D",
#         "answer",
#         "explanation",
#     }

#     if not isinstance(mcqs, list):
#         return False

#     for q in mcqs:
#         if not required_keys.issubset(q.keys()):
#             return False

#         if q["answer"] not in ["A", "B", "C", "D"]:
#             return False

#     return True


# def generate_valid_mcqs(context, max_retries=3):
#     for attempt in range(max_retries):
#         print(f"\n🔁 Attempt {attempt + 1} generating MCQs...")

#         raw_output = generate_mcqs("Entire Textbook", context)
#         cleaned = clean_llm_output(raw_output)

#         try:
#             parsed = json.loads(cleaned)

#             if not is_valid_schema(parsed):
#                 print("❌ Schema validation failed. Retrying...")
#                 continue

#             print("✅ Valid JSON + Schema generated successfully.")
#             return parsed

#         except Exception:
#             print("❌ Invalid JSON. Retrying...")

#     print("\n⚠ All attempts failed.")
#     return None

# def main():
#     print("🚀 Program started")

#     pdf_path = "textbook.pdf"

#     # ---------------------------
#     # 1️⃣ Extract Text
#     # ---------------------------
#     try:
#         print("📘 Extracting text from textbook...")
#         text = extract_text_from_pdf(pdf_path)
#         print("✅ Extraction complete")
#         print("Text length:", len(text))

#         if len(text) == 0:
#             print("⚠ PDF extraction returned empty text.")
#             return

#     except Exception as e:
#         print("❌ Error during PDF extraction:", e)
#         return

#     # ---------------------------
#     # 2️⃣ Chunk Text
#     # ---------------------------
#     try:
#         print("✂ Chunking text...")
#         chunks = chunk_text(text)
#         print(f"✅ Total chunks created: {len(chunks)}")

#         if len(chunks) == 0:
#             print("⚠ No chunks created.")
#             return

#     except Exception as e:
#         print("❌ Error during chunking:", e)
#         return

#     # ---------------------------
#     # 3️⃣ Create Embeddings (future importance use)
#     # ---------------------------
#     try:
#         print("🧠 Creating embeddings...")
#         embedding_model = get_embedding_model()
#         _ = create_vector_store(chunks, embedding_model)
#         print("✅ Embeddings stored successfully")

#     except Exception as e:
#         print("❌ Error during embedding/vector store creation:", e)
#         return

#     # ---------------------------
#     # 4️⃣ Select Content
#     # ---------------------------
#     try:
#         print("📚 Selecting content from entire textbook...")

#         sample_size = min(2, len(chunks))  # keep small for stability
#         sampled_chunks = random.sample(chunks, sample_size)

#         context = "\n\n".join(sampled_chunks)

#     except Exception as e:
#         print("❌ Error selecting chunks:", e)
#         return

#     # ---------------------------
#     # 5️⃣ Generate MCQs with Validation
#     # ---------------------------
#     print("🤖 Generating MCQs...\n")

#     mcqs = generate_valid_mcqs(context)

#     if mcqs is None:
#         print("\n❌ Failed to generate valid MCQs.")
#         return

#     print("\n================ GENERATED MCQs ================\n")
#     # print(json.dumps(mcqs, indent=2))
#     run_quiz(mcqs)


# if __name__ == "__main__":
#     main()
