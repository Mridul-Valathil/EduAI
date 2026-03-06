"""
PATCH FOR web_app.py
====================
Add these imports and route to your existing web_app.py.

Step 1 — Add to imports at top of web_app.py:
    from topic_analyzer import analyze_topics

Step 2 — In your index() POST handler, after computing module_mapping,
         add the topic analysis call shown below.

Step 3 — Add the /topics route shown below.

Step 4 — Add the Jinja2 template shown in topics.html below.
"""

# ─────────────────────────────────────────────────────────────────────────────
# ADD THIS IMPORT to web_app.py
# ─────────────────────────────────────────────────────────────────────────────
# from topic_analyzer import analyze_topics


# ─────────────────────────────────────────────────────────────────────────────
# ADD THIS to GLOBAL_DATA dict in web_app.py
# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL_DATA = {
#     "chunks": None,
#     "chunk_scores": None,
#     "modules": None,
#     "module_mapping": None,
#     "topic_analysis": None,     # ← NEW
# }


# ─────────────────────────────────────────────────────────────────────────────
# ADD THIS BLOCK inside index() POST handler
# (put it right after you store GLOBAL_DATA["module_mapping"] = module_mapping)
# ─────────────────────────────────────────────────────────────────────────────
"""
# ── Topic Analysis (Syllabus × PYQ → Priority + Summaries) ──────────────
print("\\n📊 Running topic priority analysis...")
topic_results = analyze_topics(
    syllabus_text=syllabus_text,
    pyq_text=pyq_text,
    textbook_text=textbook_text,
    generate_summaries=True,    # set False to skip LLM summaries (faster)
)
GLOBAL_DATA["topic_analysis"] = topic_results
"""


# ─────────────────────────────────────────────────────────────────────────────
# NEW FLASK ROUTE — add this to web_app.py
# ─────────────────────────────────────────────────────────────────────────────
"""
@app.route("/topics")
def topics():
    topic_analysis = GLOBAL_DATA.get("topic_analysis")

    if not topic_analysis:
        return redirect("/")

    high   = [t for t in topic_analysis if t["priority"] == "HIGH"]
    medium = [t for t in topic_analysis if t["priority"] == "MEDIUM"]
    low    = [t for t in topic_analysis if t["priority"] == "LOW"]

    return render_template(
        "topics.html",
        high=high,
        medium=medium,
        low=low,
        total=len(topic_analysis),
    )
"""
