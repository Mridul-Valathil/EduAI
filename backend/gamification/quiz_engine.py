# import json
# import random
# from generation.mcq_generator import generate_single_mcq


# def clean_output(output):
#     return output.replace("```json", "").replace("```", "").strip()


# def is_valid_question(q):
#     required = {
#         "question",
#         "option_A",
#         "option_B",
#         "option_C",
#         "option_D",
#         "answer",
#         "explanation",
#     }

#     if not isinstance(q, dict):
#         return False

#     if not required.issubset(q.keys()):
#         return False

#     if q["answer"] not in ["A", "B", "C", "D"]:
#         return False

#     return True


# def run_quiz(chunks, num_questions=3):
#     print("\n🎮 QUIZ STARTED")
#     print("Answer using A, B, C, or D.\n")

#     score = 0

#     for i in range(num_questions):
#         print(f"\n--- Generating Question {i+1} ---")

#         context = random.choice(chunks)

#         # retry per question
#         for attempt in range(3):
#             raw = generate_single_mcq(context)
#             cleaned = clean_output(raw)

#             try:
#                 parsed = json.loads(cleaned)

#                 if is_valid_question(parsed):
#                     question = parsed
#                     break
#                 else:
#                     print("❌ Schema invalid. Retrying...")
#             except Exception:
#                 print("❌ JSON invalid. Retrying...")
#         else:
#             print("⚠ Failed to generate valid question. Skipping.")
#             continue

#         print("\n" + question["question"])
#         print(f"A) {question['option_A']}")
#         print(f"B) {question['option_B']}")
#         print(f"C) {question['option_C']}")
#         print(f"D) {question['option_D']}")

#         user_answer = input("\nYour answer: ").strip().upper()

#         if user_answer == question["answer"]:
#             print("✅ Correct!")
#             score += 1
#         else:
#             print(f"❌ Wrong! Correct answer: {question['answer']}")

#         print("💡", question["explanation"])

#     print("\n====================")
#     print("🎉 QUIZ FINISHED")
#     print("====================")
#     print(f"Score: {score}/{num_questions}")
#     print(f"Accuracy: {round((score/num_questions)*100,2)}%")

import json
import random
import re
from generation.mcq_generator import generate_single_mcq


# ---------------------------------------------------
# Utility: Clean LLM Output
# ---------------------------------------------------
def clean_output(output):
    return output.replace("```json", "").replace("```", "").strip()


# ---------------------------------------------------
# Utility: Validate MCQ Schema
# ---------------------------------------------------
def is_valid_question(q):
    required_keys = {
        "question",
        "option_A",
        "option_B",
        "option_C",
        "option_D",
        "answer",
        "explanation",
    }

    if not isinstance(q, dict):
        return False

    if not required_keys.issubset(q.keys()):
        return False

    if q["answer"] not in ["A", "B", "C", "D"]:
        return False

    return True


# ---------------------------------------------------
# Importance-Weighted Chunk Selection
# ---------------------------------------------------
def weighted_chunk_selection(chunks, chunk_scores):
    weights = []

    for score in chunk_scores:
        if score >= 3:
            weights.append(5)   # HIGH
        elif score == 2:
            weights.append(3)   # MEDIUM
        elif score == 1:
            weights.append(2)   # LOW+
        else:
            weights.append(1)   # LOW

    # random.choices returns a list → take first element
    return random.choices(chunks, weights=weights, k=1)[0]


# ---------------------------------------------------
# Main Quiz Engine
# ---------------------------------------------------
def run_quiz(chunks, chunk_scores, num_questions=5):
    print("🎮 QUIZ STARTED")
    print("Answer using A, B, C, or D.\n")

    score = 0

    for i in range(num_questions):
        print(f"\n==============================")
        print(f"Generating Question {i+1}/{num_questions}")
        print("==============================")

        # Select chunk using importance weighting
        context = weighted_chunk_selection(chunks, chunk_scores)

        # Retry generation per question
        question = None

        for attempt in range(3):
            raw_output = generate_single_mcq(context)
            cleaned = clean_output(raw_output)

            try:
                parsed = json.loads(cleaned)

                if is_valid_question(parsed):
                    question = parsed
                    break
                else:
                    print("⚠ Schema invalid. Retrying...")
            except Exception:
                print("⚠ JSON invalid. Retrying...")

        if question is None:
            print("❌ Failed to generate valid question. Skipping.")
            continue

        # Display question
        print("\n" + question["question"])
        print(f"A) {question['option_A']}")
        print(f"B) {question['option_B']}")
        print(f"C) {question['option_C']}")
        print(f"D) {question['option_D']}")

        user_answer = input("\nYour answer: ").strip().upper()

        if user_answer == question["answer"]:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Wrong! Correct answer: {question['answer']}")

        print("💡 Explanation:", question["explanation"])

    # ---------------------------------------------------
    # Final Results
    # ---------------------------------------------------
    print("\n===================================")
    print("🎉 QUIZ COMPLETED")
    print("===================================")

    print(f"Score: {score}/{num_questions}")
    accuracy = round((score / num_questions) * 100, 2)
    print(f"Accuracy: {accuracy}%")

    if accuracy == 100:
        print("🏆 Outstanding Performance!")
    elif accuracy >= 60:
        print("👍 Good Job! Keep Practicing.")
    else:
        print("📚 Focus more on HIGH importance topics.")