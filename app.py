"""
app.py
-------
ConceptCheckmate — Flask backend.

Routes:
  GET  /                  -> dashboard UI
  GET  /api/topics        -> list of preloaded demo topics
  POST /api/analyze       -> run the full NLP pipeline on a transcript
  GET  /api/health        -> engine status (useful to show the interviewer
                              which similarity engine is active)
"""

from flask import Flask, render_template, request, jsonify

from nlp_engine import analyze_answer, ENGINE_MODE
from topics_data import list_topics, get_topic

app = Flask(__name__)

try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    # CORS is only needed if the frontend is ever served from a different
    # origin than the Flask app. Not required for the standard same-origin
    # setup used by this project (index.html is served by Flask itself).
    pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "engine_mode": ENGINE_MODE})


@app.route("/api/topics")
def topics():
    return jsonify(list_topics())


@app.route("/api/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(force=True, silent=True) or {}
    transcript = (payload.get("transcript") or "").strip()
    topic_id = payload.get("topic_id")
    custom_title = (payload.get("custom_title") or "").strip()
    custom_ideal_answer = (payload.get("custom_ideal_answer") or "").strip()

    if not transcript:
        return jsonify({"error": "No transcript provided. Speak or type your explanation first."}), 400

    if topic_id:
        topic = get_topic(topic_id)
        if not topic:
            return jsonify({"error": f"Unknown topic_id '{topic_id}'."}), 400
    elif custom_ideal_answer:
        # On-the-fly topic: interviewer can type ANY ideal answer and the
        # engine will auto-derive rough "key concepts" from its sentences.
        sentences = [s.strip() for s in custom_ideal_answer.replace("\n", " ").split(".") if s.strip()]
        topic = {
            "title": custom_title or "Custom Topic",
            "ideal_answer": custom_ideal_answer,
            "key_concepts": [
                {
                    "id": f"c{i}",
                    "label": (s[:40] + "…") if len(s) > 40 else s,
                    "keywords": [w for w in s.lower().split() if len(w) > 4][:6] or s.lower().split()[:3],
                }
                for i, s in enumerate(sentences[:8])
            ],
            "misconceptions": [],
        }
    else:
        return jsonify({"error": "Provide either topic_id or a custom_ideal_answer."}), 400

    result = analyze_answer(transcript, topic)
    result["topic_title"] = topic["title"]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
