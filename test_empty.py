import os
import sys

# Add backend directory to path
sys.path.append(os.path.abspath('backend'))

from backend.topic_analyzer import analyze_topics

syllabus_text = "   \n"  # Empty syllabus
textbook_text = "Software engineering is the application of engineering to the development of software in a systematic method. Agile is a methodology."
pyq_text = "What is agile methodology? Explain waterfall model."

print("Running analyze_topics with EMPTY syllabus...")
try:
    results = analyze_topics(syllabus_text, pyq_text, textbook_text, generate_summaries=False)
    print("RESULTS:")
    import json
    print(json.dumps(results, indent=2))
except Exception as e:
    print(f"EXCEPTION CAUGHT: {e}")
    import traceback
    traceback.print_exc()
