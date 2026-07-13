# ConceptCheckmate

Live: https://concept-checkmate.vercel.app/

### An AI system that listens to a student's spoken explanation, checks true understanding, and gives personalized feedback.

---

## 1. Quick Setup (5 minutes)

```bash
cd concept-checkmate
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in **Google Chrome** (Web Speech API works best there).

That's it — no API keys, no external services, no internet dependency at runtime.
This was a deliberate design choice so nothing can fail live in front of an interviewer.

### Optional "pro mode" (do this only if you have spare time before the interview)
Uncomment the last two lines in `requirements.txt` and run:
```bash
pip install sentence-transformers nltk
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"
```
The app auto-detects these and upgrades from TF-IDF similarity to real
`all-MiniLM-L6-v2` sentence embeddings — check the badge in the top-right
corner of the UI, it tells you (and the interviewer) which engine is live.

---

## 2. What you built — map to your architecture diagram

| Your diagram stage | Implementation |
|---|---|
| Voice Input | Browser microphone via `MediaDevices` |
| Speech Recognition (Whisper/Google API) | **Web Speech API** (`webkitSpeechRecognition`) — real-time, in-browser, zero server round trips. `nlp_engine.py` docstring explains how to swap in Whisper server-side if asked. |
| Converted Text | Live transcript box (also editable/typeable — resilient if mic fails on stage) |
| NLP Preprocessing | `nlp_engine.preprocess()` — lowercasing, punctuation stripping, tokenization, stopword removal, lemmatization (NLTK if available, hand-rolled fallback otherwise) |
| Concept Understanding | `nlp_engine._semantic_similarity` / `_best_sentence_match` — Sentence-Transformer embeddings, with a TF-IDF vector-space fallback |
| Compare with Ideal Answer | Cosine similarity between student transcript and a curated "ideal answer" per topic |
| Similarity + Missing Concepts | Per-concept sentence matching against a **key-concept bank** (`topics_data.py`) → matched / partially explained / missing, plus **misconception pattern detection** |
| AI Feedback Generator | `nlp_engine.generate_feedback()` — deterministic templated coaching text (swap-in point clearly marked for an LLM API call if you want to extend it) |
| Dashboard + Report + Score | Flask + vanilla JS dashboard: radial mastery gauge, color-coded concept chips, misconception callouts, downloadable `.txt` report |

---

## 3. Live demo script (2–3 minutes, rehearse this)

1. **Open the app**, point out the engine-status badge — "this shows which
   similarity engine is active; the system degrades gracefully from
   transformer embeddings to TF-IDF so it never breaks in production."
2. **Pick a preloaded topic** (e.g. OOP) and either:
   - Click **Start speaking** and explain it out loud, deliberately leaving
     out "Polymorphism" and saying *"a class and an object are the same
     thing"* — a seeded misconception you know the system will catch. **or**
   - Type/paste the transcript if the room's mic/wifi is unreliable.
3. Click **Analyze Understanding** — walk through the report live:
   - the gauge + score
   - concepts covered vs missing (in **your own words**, not just green/red)
   - the misconception callout — *"the model isn't just checking keyword
     overlap, it flagged a specific factual error"*
   - the personalized feedback paragraph
4. **Switch to "+ Custom topic"** and type any topic the interviewer names
   on the spot with a short ideal answer, then have them (or you) explain
   it. This proves the system isn't hardcoded to a demo script — it's a
   general-purpose comparator.

---

## 4. Talking points if they probe deeper

- **"Why not just call an LLM API for everything?"**
  Cost, latency, and reliability at scale — this hybrid approach uses cheap
  deterministic NLP for the 90% case (concept coverage, similarity scoring)
  and reserves a clearly marked seam (`generate_feedback()`) where an LLM
  call could add richer free-text coaching for the remaining 10%.
- **"How would you scale this?"**
  Precompute topic embeddings offline and cache them; move the model to a
  small inference service (FastAPI + batching) behind the Flask app;
  containerize with Docker; store session transcripts + scores in Postgres
  for a teacher-facing analytics dashboard.
- **"How would you improve concept-gap detection?"**
  Fine-tune a sentence-similarity model on a labeled dataset of
  student-answer/ideal-answer pairs per subject; add negation-aware NLI
  (Natural Language Inference) models to detect contradictions more
  robustly than the current keyword-pattern misconception bank.
- **"What about non-English or accented speech?"**
  Web Speech API supports many `lang` codes; swapping to a Whisper
  server-side pipeline (mentioned in the docstring) would improve accuracy
  for noisy/accented audio and enable offline/batch grading.
- **"Multi-user / production concerns?"**
  Add auth, per-student history, rate limiting, and a proper WSGI server
  (gunicorn) instead of Flask's dev server — noted directly in `app.py`.

---

## 5. Files

```
concept-checkmate/
├── app.py              Flask routes / API
├── nlp_engine.py        preprocessing, similarity, scoring, feedback generation
├── topics_data.py      5 preloaded topics (OOP, OSI Model, Normalization,
│                        Photosynthesis, ML Fundamentals) — add your own!
├── requirements.txt
├── templates/index.html
└── static/{style.css, script.js}
```

Add a topic in under a minute: copy a block in `topics_data.py`, list its
`key_concepts` with a few keyword synonyms each, optionally add
`misconceptions`. No code changes needed elsewhere.

Good luck — you've got this. 🎯
