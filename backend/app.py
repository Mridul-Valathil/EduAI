

# from preprocessing.pdf_extractor import extract_text_from_pdf
# from preprocessing.chunker import chunk_text
# from vector_db.embedding_model import get_embedding_model
# from vector_db.vector_store import create_vector_store
# from gamification.quiz_engine import run_quiz


# def main():
#     print("🚀 Program started")

#     pdf_path = "textbook.pdf"

#     # 1️⃣ Extract Text
#     print("📘 Extracting text from textbook...")
#     text = extract_text_from_pdf(pdf_path)

#     if not text:
#         print("❌ Failed to extract text.")
#         return

#     print("✅ Extraction complete")

#     # 2️⃣ Chunk Text
#     print("✂ Chunking text...")
#     chunks = chunk_text(text)

#     if not chunks:
#         print("❌ No chunks created.")
#         return

#     print(f"✅ Total chunks created: {len(chunks)}")

#     # 3️⃣ Create Embeddings (for future importance engine)
#     print("🧠 Creating embeddings...")
#     embedding_model = get_embedding_model()
#     create_vector_store(chunks, embedding_model)
#     print("✅ Embeddings stored successfully")

#     # 4️⃣ Start Dynamic Quiz (generation inside loop)
#     run_quiz(chunks, num_questions=3)


# if __name__ == "__main__":
#     main()


# ===pyq test

# from pyq_engine.pyq_parser import extract_pyq_text, extract_questions_with_llm, extract_questions_with_regex

# pdf_to_parse = "pyq.pdf" # Or "bio.pdf"
# pyq_text = extract_pyq_text(pdf_to_parse)

# # You can use extract_questions_with_regex for fast testing (23 questions) 
# # or extract_questions_with_llm for slow but accurate multi-format parsing.
# print(f"\n--- Starting Semantic LLM Question Extraction on {pdf_to_parse} ---")
# questions = extract_questions_with_llm(pyq_text)

# print("\nTotal PYQ Questions Extracted:", len(questions))

# for i, q in enumerate(questions[:5], 1):
#     print(f"\nQ{i}:\n{q}")




# from preprocessing.pdf_extractor import extract_text_from_pdf
# from preprocessing.chunker import chunk_text
# from vector_db.embedding_model import get_embedding_model

# from pyq_engine.pyq_parser import (
#     extract_pyq_text,
#     extract_questions_with_regex
# )

# from importance_engine.importance_calculator import (
#     calculate_chunk_scores,
#     classify_importance
# )


# def main():
#     print("🚀 Starting Curriculum-Aligned Importance Engine\n")

#     # ---------------------------
#     # 1️⃣ Load Textbook
#     # ---------------------------
#     textbook_path = "textbook.pdf"
#     print("📘 Extracting textbook...")
#     textbook_text = extract_text_from_pdf(textbook_path)

#     if not textbook_text:
#         print("❌ Failed to extract textbook.")
#         return

#     print("✅ Textbook extracted.")

#     # ---------------------------
#     # 2️⃣ Chunk Textbook
#     # ---------------------------
#     print("✂ Chunking textbook...")
#     chunks = chunk_text(textbook_text)

#     if not chunks:
#         print("❌ No chunks created.")
#         return

#     print(f"✅ Total textbook chunks: {len(chunks)}")

#     # ---------------------------
#     # 3️⃣ Load PYQ
#     # ---------------------------
#     pyq_path = "pyq.pdf"
#     print("\n📄 Extracting PYQ...")
#     pyq_text = extract_pyq_text(pyq_path)

#     if not pyq_text:
#         print("❌ Failed to extract PYQ.")
#         return

#     print("✅ PYQ extracted.")

#     # ---------------------------
#     # 4️⃣ Extract Questions (Regex)
#     # ---------------------------
#     print("🔍 Extracting questions using regex...")
#     questions = extract_questions_with_regex(pyq_text)

#     print(f"✅ Total PYQ questions extracted: {len(questions)}")

#     if len(questions) == 0:
#         print("❌ No questions extracted.")
#         return

#     # ---------------------------
#     # 5️⃣ Create Embeddings
#     # ---------------------------
#     print("\n🧠 Generating embeddings...")
#     embedding_model = get_embedding_model()

#     print("   → Embedding textbook chunks...")
#     chunk_embeddings = embedding_model.embed_documents(chunks)

#     print("   → Embedding PYQ questions...")
#     pyq_embeddings = embedding_model.embed_documents(questions)

#     print("✅ Embeddings generated.")

#     # ---------------------------
#     # 6️⃣ Calculate Importance
#     # ---------------------------
#     print("\n📊 Calculating semantic similarity...")

#     chunk_scores = calculate_chunk_scores(
#         pyq_embeddings,
#         chunk_embeddings,
#         threshold=0.6
#     )

#     importance_labels = classify_importance(chunk_scores)

#     # ---------------------------
#     # 7️⃣ Display Results
#     # ---------------------------
#     print("\n================ IMPORTANCE ANALYSIS ================\n")

#     for i in range(len(chunks)):
#         print(
#             f"Chunk {i+1} | "
#             f"Score: {chunk_scores[i]} | "
#             f"Importance: {importance_labels[i]}"
#         )

#     print("\n🎯 Importance Engine Completed Successfully.\n")


# if __name__ == "__main__":
#     main()



from preprocessing.pdf_extractor import extract_text_from_pdf
from preprocessing.chunker import chunk_text
from vector_db.embedding_model import get_embedding_model

from pyq_engine.pyq_parser import (
    extract_pyq_text,
    extract_questions_with_regex
)

from importance_engine.importance_calculator import (
    calculate_chunk_scores,
    classify_importance
)

from gamification.quiz_engine import run_quiz


def main():
    print("🚀 Starting Curriculum-Aligned Intelligent Learning Assistant\n")

    # ---------------------------
    # 1️⃣ Load Textbook
    # ---------------------------
    textbook_path = "textbook.pdf"
    print("📘 Extracting textbook...")
    textbook_text = extract_text_from_pdf(textbook_path)

    if not textbook_text:
        print("❌ Failed to extract textbook.")
        return

    print("✅ Textbook extracted.")

    # ---------------------------
    # 2️⃣ Chunk Textbook
    # ---------------------------
    print("✂ Chunking textbook...")
    chunks = chunk_text(textbook_text)

    if not chunks:
        print("❌ No chunks created.")
        return

    print(f"✅ Total textbook chunks: {len(chunks)}")

    # ---------------------------
    # 3️⃣ Load PYQ
    # ---------------------------
    pyq_path = "pyq.pdf"
    print("\n📄 Extracting PYQ...")
    pyq_text = extract_pyq_text(pyq_path)

    if not pyq_text:
        print("❌ Failed to extract PYQ.")
        return

    print("✅ PYQ extracted.")

    # ---------------------------
    # 4️⃣ Extract Questions (Regex)
    # ---------------------------
    print("🔍 Extracting questions using regex...")
    questions = extract_questions_with_regex(pyq_text)

    print(f"✅ Total PYQ questions extracted: {len(questions)}")

    if len(questions) == 0:
        print("❌ No questions extracted.")
        return

    # ---------------------------
    # 5️⃣ Generate Embeddings
    # ---------------------------
    print("\n🧠 Generating embeddings...")
    embedding_model = get_embedding_model()

    print("   → Embedding textbook chunks...")
    chunk_embeddings = embedding_model.embed_documents(chunks)

    print("   → Embedding PYQ questions...")
    pyq_embeddings = embedding_model.embed_documents(questions)

    print("✅ Embeddings generated.")

    # ---------------------------
    # 6️⃣ Calculate Importance
    # ---------------------------
    print("\n📊 Calculating semantic similarity...")

    chunk_scores = calculate_chunk_scores(
        pyq_embeddings,
        chunk_embeddings,
        threshold=0.6
    )

    importance_labels = classify_importance(chunk_scores)

    # ---------------------------
    # 7️⃣ Visualize Importance (Sorted)
    # ---------------------------
    print("\n================ IMPORTANCE ANALYSIS ================\n")

    chunk_info = []

    for i in range(len(chunks)):
        chunk_info.append({
            "index": i,
            "score": chunk_scores[i],
            "importance": importance_labels[i],
            "preview": chunks[i][:120].replace("\n", " ") + "..."
        })

    # Sort by score descending
    chunk_info = sorted(chunk_info, key=lambda x: x["score"], reverse=True)

    for item in chunk_info:
        print(
            f"Chunk {item['index']+1} | "
            f"Score: {item['score']} | "
            f"{item['importance']}\n"
            f"Preview: {item['preview']}\n"
        )

    # ---------------------------
    # 8️⃣ Start Importance-Weighted Quiz
    # ---------------------------
    print("\n🎮 Starting Importance-Weighted Quiz...\n")

    run_quiz(
        chunks,
        chunk_scores,
        num_questions=5
    )

    print("\n🎯 Session Completed Successfully.\n")


if __name__ == "__main__":
    main()