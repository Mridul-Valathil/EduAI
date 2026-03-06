from flask import Flask, render_template, request, jsonify, session
import os
import json
import random

from syllabus_engine.syllabus_parser import extract_modules_from_syllabus
from preprocessing.pdf_extractor import extract_text_from_pdf
from preprocessing.chunker import chunk_text
from vector_db.embedding_model import get_embedding_model
from pyq_engine.pyq_parser import extract_questions_with_regex, extract_questions_with_llm
from importance_engine.importance_calculator import calculate_chunk_scores
from generation.mcq_generator import generate_single_mcq
from generation.mock_generator import generate_mock_paper
from topic_analyzer import analyze_topics

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GLOBAL_DATA = {
    "chunks": None,
    "chunk_scores": None,
    "modules": None,
    "module_mapping": None,
    "topic_analysis": None,
}


def weighted_chunk_selection(chunks, chunk_scores):
    weights = []
    for score in chunk_scores:
        if score >= 3:
            weights.append(5)
        elif score == 2:
            weights.append(3)
        elif score == 1:
            weights.append(2)
        else:
            weights.append(1)
    return random.choices(chunks, weights=weights, k=1)[0]


@app.route("/", methods=["GET"])
def index():
    # Only clear the uploaded flag if no data has been processed
    if GLOBAL_DATA.get("chunks") is None:
        session["uploaded"] = False
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({
        "uploaded": session.get("uploaded", False),
    })


@app.route("/api/upload", methods=["POST"])
def api_upload():
    try:
        textbook_file = request.files["textbook"]
        pyq_files = request.files.getlist("pyq")
        syllabus_file = request.files["syllabus"]
        difficulty = request.form.get("difficulty", "Medium")

        textbook_path = os.path.join(UPLOAD_FOLDER, "textbook.pdf")
        syllabus_path = os.path.join(UPLOAD_FOLDER, "syllabus.pdf")

        textbook_file.save(textbook_path)
        syllabus_file.save(syllabus_path)

        # ----------------------------
        # Extract Textbook
        # ----------------------------
        textbook_text = extract_text_from_pdf(textbook_path)
        chunks = chunk_text(textbook_text)

        # ----------------------------
        # Extract PYQ(s)
        # ----------------------------
        pyq_text = ""
        for i, p_file in enumerate(pyq_files):
            if p_file.filename:
                p_path = os.path.join(UPLOAD_FOLDER, f"pyq_{i}.pdf")
                p_file.save(p_path)
                pyq_text += extract_text_from_pdf(p_path) + "\n\n"
                
        # Use LLM for dynamic question extraction
        questions = extract_questions_with_llm(pyq_text)

        # ----------------------------
        # Extract Syllabus
        # ----------------------------
        syllabus_text = extract_text_from_pdf(syllabus_path)
        modules = extract_modules_from_syllabus(syllabus_text)

        # ----------------------------
        # Embeddings
        # ----------------------------
        embedding_model = get_embedding_model()
        chunk_embeddings = embedding_model.embed_documents(chunks)
        pyq_embeddings = embedding_model.embed_documents(questions)

        # ----------------------------
        # Chunk-Level Importance
        # ----------------------------
        chunk_scores = calculate_chunk_scores(
            pyq_embeddings,
            chunk_embeddings,
            threshold=0.6
        )

        # ---------------------------------------------------
        # MODULE SEMANTIC MAPPING
        # ---------------------------------------------------
        module_mapping = {}
        module_texts = list(modules.values())
        module_names = list(modules.keys())
        module_embeddings = embedding_model.embed_documents(module_texts)

        for i, module_name in enumerate(module_names):
            module_mapping[module_name] = {
                "chunk_indices": [],
                "pyq_score": 0,
                "coverage_score": 0
            }
            for j, chunk_embedding in enumerate(chunk_embeddings):
                similarity = sum(
                    a * b for a, b in zip(module_embeddings[i], chunk_embedding)
                )
                if similarity > 0.6:
                    module_mapping[module_name]["chunk_indices"].append(j)
                    module_mapping[module_name]["pyq_score"] += chunk_scores[j]
                    module_mapping[module_name]["coverage_score"] += 1

        # ---------------------------------------------------
        # NORMALIZE + HYBRID SCORE
        # ---------------------------------------------------
        max_pyq = max((data["pyq_score"] for data in module_mapping.values()), default=1) or 1
        max_coverage = max((data["coverage_score"] for data in module_mapping.values()), default=1) or 1

        for module, data in module_mapping.items():
            norm_pyq = data["pyq_score"] / max_pyq
            norm_cov = data["coverage_score"] / max_coverage
            final_score = (0.7 * norm_pyq) + (0.3 * norm_cov)
            data["normalized_score"] = round(final_score, 2)

        for module, data in module_mapping.items():
            score = data["normalized_score"]
            if score >= 0.66:
                level = "HIGH"
            elif score >= 0.33:
                level = "MEDIUM"
            else:
                level = "LOW"
            data["level"] = level

        # ----------------------------
        # Store in GLOBAL_DATA
        # ----------------------------
        GLOBAL_DATA["chunks"] = chunks
        GLOBAL_DATA["chunk_scores"] = chunk_scores
        GLOBAL_DATA["modules"] = modules
        GLOBAL_DATA["module_mapping"] = module_mapping
        
        # Save raw texts for deferred processing
        GLOBAL_DATA["syllabus_text"] = syllabus_text
        GLOBAL_DATA["pyq_text"] = pyq_text
        GLOBAL_DATA["textbook_text"] = textbook_text
        
        # Clear old topic analysis if any
        GLOBAL_DATA["topic_analysis"] = None

        session["uploaded"] = True
        session["difficulty"] = difficulty
        
        return jsonify({"status": "success", "message": "Files processed successfully"})
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/topics", methods=["GET"])
def api_topics():
    if not session.get("uploaded"):
        return jsonify({"status": "error", "message": "Files not uploaded yet."}), 400

    if GLOBAL_DATA.get("topic_analysis") is None:
        if GLOBAL_DATA.get("syllabus_text") and GLOBAL_DATA.get("pyq_text") and GLOBAL_DATA.get("textbook_text"):
            print("\n📊 Running deferred topic priority analysis...")
            topic_results = analyze_topics(
                syllabus_text=GLOBAL_DATA["syllabus_text"],
                pyq_text=GLOBAL_DATA["pyq_text"],
                textbook_text=GLOBAL_DATA["textbook_text"],
                generate_summaries=True,
            )
            GLOBAL_DATA["topic_analysis"] = topic_results
        else:
            return jsonify({"status": "error", "message": "Missing text data for analysis."}), 400

    topic_analysis = GLOBAL_DATA.get("topic_analysis")
    high   = [t for t in topic_analysis if t["priority"] == "HIGH"]
    medium = [t for t in topic_analysis if t["priority"] == "MEDIUM"]
    low    = [t for t in topic_analysis if t["priority"] == "LOW"]

    return jsonify({
        "status": "success",
        "data": {
            "high": high,
            "medium": medium,
            "low": low,
            "total": len(topic_analysis)
        }
    })


@app.route("/api/quiz/generate", methods=["GET"])
def api_quiz_generate():
    if GLOBAL_DATA.get("chunks") is None:
        return jsonify({"status": "error", "message": "No data available."}), 400

    chunks = GLOBAL_DATA["chunks"]
    chunk_scores = GLOBAL_DATA["chunk_scores"]
    difficulty = session.get("difficulty", "Medium")

    question = None
    for _ in range(5):  # retry up to 5 times
        context = weighted_chunk_selection(chunks, chunk_scores)
        raw_output = generate_single_mcq(context, difficulty=difficulty)
        cleaned = raw_output.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(cleaned)
            if (
                isinstance(parsed, dict)
                and "question" in parsed
                and "option_A" in parsed
                and "option_B" in parsed
                and "option_C" in parsed
                and "option_D" in parsed
                and "answer" in parsed
                and parsed["answer"] in ["A", "B", "C", "D"]
            ):
                question = parsed
                break
        except Exception:
            continue

    if question is None:
        return jsonify({"status": "error", "message": "Failed to generate question."}), 500

    # Save correct answer in session securely
    session["current_quiz_answer"] = question["answer"]
    session["current_quiz_explanation"] = question.get("explanation", "No explanation provided.")

    # Return question without the answer
    return jsonify({
        "status": "success",
        "data": {
            "question": question["question"],
            "option_A": question["option_A"],
            "option_B": question["option_B"],
            "option_C": question["option_C"],
            "option_D": question["option_D"],
        }
    })


@app.route("/api/quiz/answer", methods=["POST"])
def api_quiz_answer():
    data = request.json
    user_answer = data.get("answer")
    correct_answer = session.get("current_quiz_answer")
    explanation = session.get("current_quiz_explanation")

    is_correct = (user_answer == correct_answer)

    return jsonify({
        "status": "success",
        "data": {
            "correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": explanation
        }
    })


@app.route("/api/mock", methods=["GET"])
def api_mock():
    if GLOBAL_DATA.get("chunks") is None:
        return jsonify({"status": "error", "message": "No data available."}), 400

    textbook_chunks = GLOBAL_DATA["chunks"]
    pyq_text = GLOBAL_DATA.get("pyq_text", "")

    paper = generate_mock_paper(pyq_text, textbook_chunks)

    return jsonify({
        "status": "success",
        "data": {
            "paper": paper
        }
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)