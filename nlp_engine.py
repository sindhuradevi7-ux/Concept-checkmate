"""
nlp_engine.py
--------------
Core analysis pipeline for ConceptCheckmate.

Pipeline stages (mirrors the architecture diagram):
  1. NLP Preprocessing      -> tokenize, remove stopwords, lemmatize
  2. Concept Understanding  -> embed / vectorize student + ideal answer
  3. Compare with Ideal     -> cosine similarity (overall + per-concept)
  4. Gap Analysis           -> missing concepts + misconception detection
  5. Feedback Generation    -> personalized, actionable feedback + score

Design note for reliability during a live demo:
  Sentence-Transformers (real semantic embeddings) is used WHEN AVAILABLE,
  but the engine transparently falls back to a TF-IDF + cosine-similarity
  model (scikit-learn, pure CPU, no model download, no internet) so the
  project never breaks on stage because of a missing model download.
  `ENGINE_MODE` tells you (and the interviewer) which one is active.
"""

import re
import string
from difflib import SequenceMatcher

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------------
# Optional heavy dependencies — loaded lazily and gracefully degraded.
# --------------------------------------------------------------------------
ENGINE_MODE = "tfidf"          # will flip to "sentence-transformers" if available
_ST_MODEL = None

try:
    from sentence_transformers import SentenceTransformer
    _ST_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    ENGINE_MODE = "sentence-transformers"
except Exception:
    _ST_MODEL = None
    ENGINE_MODE = "tfidf"

try:
    import nltk
    from nltk.corpus import stopwords as nltk_stopwords
    from nltk.stem import WordNetLemmatizer
    _ = nltk_stopwords.words("english")
    _lemmatizer = WordNetLemmatizer()
    _lemmatizer.lemmatize("testing")
    _NLTK_READY = True
except Exception:
    _NLTK_READY = False

# --------------------------------------------------------------------------
# Lightweight built-in fallback so the pipeline NEVER crashes without
# internet / nltk downloads on interview day.
# --------------------------------------------------------------------------
_BASIC_STOPWORDS = set("""
a an the is are was were be been being am i you he she it we they this that
these those of in on at to for with and or but if then so because as by from
about into over under again further once here there all any both each few
more most other some such no nor not only own same than too very s t can will
just don should now do does did doing have has had having my your his her its
our their what which who whom
""".split())


def _basic_lemmatize(word):
    """Very small suffix-stripping fallback lemmatizer."""
    for suf in ("ings", "ing", "edly", "ed", "ies", "es", "s"):
        if word.endswith(suf) and len(word) - len(suf) > 2:
            return word[: -len(suf)] + ("y" if suf == "ies" else "")
    return word


def preprocess(text):
    """
    Stage: NLP Preprocessing
    Returns (clean_text, tokens) after tokenization, stopword removal
    and lemmatization. Uses nltk if available, else the built-in fallback.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    raw_tokens = text.split()

    if _NLTK_READY:
        stop_set = set(nltk_stopwords.words("english"))
        tokens = [_lemmatizer.lemmatize(t) for t in raw_tokens if t not in stop_set and len(t) > 1]
    else:
        tokens = [_basic_lemmatize(t) for t in raw_tokens if t not in _BASIC_STOPWORDS and len(t) > 1]

    return " ".join(tokens), tokens


def _split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _embed(sentences):
    """Return an embedding matrix for a list of strings, using whichever
    engine is active."""
    if ENGINE_MODE == "sentence-transformers":
        return np.array(_ST_MODEL.encode(sentences))
    # TF-IDF fallback needs a shared vocabulary — caller must fit jointly.
    raise RuntimeError("Use _tfidf_similarity for tfidf mode")


def _semantic_similarity(text_a, text_b):
    """Overall similarity between two full texts, 0-1."""
    if not text_a.strip() or not text_b.strip():
        return 0.0
    if ENGINE_MODE == "sentence-transformers":
        emb = _ST_MODEL.encode([text_a, text_b])
        sim = cosine_similarity([emb[0]], [emb[1]])[0][0]
        return float(max(0.0, min(1.0, sim)))
    vec = TfidfVectorizer().fit([text_a, text_b])
    mat = vec.transform([text_a, text_b])
    sim = cosine_similarity(mat[0], mat[1])[0][0]
    return float(max(0.0, min(1.0, sim)))


def _best_sentence_match(concept_sentence, student_sentences):
    """Find the student sentence most semantically similar to a concept
    sentence, returning (best_score, best_sentence)."""
    if not student_sentences:
        return 0.0, ""
    if ENGINE_MODE == "sentence-transformers":
        emb = _ST_MODEL.encode([concept_sentence] + student_sentences)
        concept_vec, student_vecs = emb[0:1], emb[1:]
        sims = cosine_similarity(concept_vec, student_vecs)[0]
    else:
        vec = TfidfVectorizer().fit([concept_sentence] + student_sentences)
        mat = vec.transform([concept_sentence] + student_sentences)
        sims = cosine_similarity(mat[0:1], mat[1:])[0]
    best_idx = int(np.argmax(sims))
    return float(sims[best_idx]), student_sentences[best_idx]


def _keyword_hit(keywords, student_text_lower):
    return any(kw.lower() in student_text_lower for kw in keywords)


def detect_misconceptions(student_text_lower, misconceptions):
    """Simple pattern-based misconception flagging: if ALL tokens of a
    misconception pattern appear in the student's answer, flag it."""
    hits = []
    for m in misconceptions:
        if all(tok.lower() in student_text_lower for tok in m["pattern"]):
            hits.append(m["note"])
    return hits


def analyze_answer(student_text, topic):
    """
    Full pipeline: preprocess -> compare -> gap analysis -> score.
    `topic` is a dict from topics_data.TOPICS (or an ad-hoc topic built
    from a custom ideal answer typed on the spot).
    Returns a structured result dict ready to be JSON-serialized.
    """
    clean_text, tokens = preprocess(student_text)
    student_sentences = _split_sentences(student_text)
    student_lower = student_text.lower()

    # --- overall semantic similarity vs the ideal answer -----------------
    overall_similarity = _semantic_similarity(student_text, topic["ideal_answer"])

    # --- per-concept coverage ---------------------------------------------
    matched, partial, missing = [], [], []
    for concept in topic["key_concepts"]:
        concept_sentence = concept["label"] + ": " + " ".join(concept["keywords"][:3])
        sim_score, best_sentence = _best_sentence_match(concept_sentence, student_sentences)
        keyword_found = _keyword_hit(concept["keywords"], student_lower)

        # Combine lexical + semantic evidence for robustness
        if keyword_found or sim_score >= 0.45:
            confidence = max(sim_score, 0.75 if keyword_found else 0.0)
            matched.append({
                "id": concept["id"],
                "label": concept["label"],
                "confidence": round(confidence, 2),
                "evidence": best_sentence[:160],
            })
        elif sim_score >= 0.25:
            partial.append({
                "id": concept["id"],
                "label": concept["label"],
                "confidence": round(sim_score, 2),
                "evidence": best_sentence[:160],
            })
        else:
            missing.append({"id": concept["id"], "label": concept["label"]})

    # --- misconceptions ------------------------------------------------
    misconceptions = detect_misconceptions(student_lower, topic.get("misconceptions", []))

    # --- scoring ---------------------------------------------------------
    total_concepts = max(len(topic["key_concepts"]), 1)
    coverage_score = (len(matched) + 0.5 * len(partial)) / total_concepts  # 0-1
    final_score = round((0.6 * coverage_score + 0.4 * overall_similarity) * 100)
    final_score = max(0, min(100, final_score - 5 * len(misconceptions)))

    if final_score >= 85:
        band = "Excellent"
    elif final_score >= 65:
        band = "Good"
    elif final_score >= 40:
        band = "Needs Improvement"
    else:
        band = "Weak"

    feedback = generate_feedback(topic, matched, partial, missing, misconceptions, final_score, band)

    return {
        "engine_mode": ENGINE_MODE,
        "score": final_score,
        "band": band,
        "overall_similarity": round(overall_similarity * 100),
        "matched_concepts": matched,
        "partial_concepts": partial,
        "missing_concepts": missing,
        "misconceptions": misconceptions,
        "feedback": feedback,
        "preprocessed_token_count": len(tokens),
        "student_sentence_count": len(student_sentences),
    }


def generate_feedback(topic, matched, partial, missing, misconceptions, score, band):
    """
    Stage: AI Feedback Generator
    Template-based natural-language feedback (deterministic, demo-safe).
    This function is intentionally the single seam where a call to an LLM
    API (OpenAI / Claude) could be dropped in for even richer, free-text
    coaching — see README for the optional upgrade.
    """
    lines = []
    lines.append(f"Overall, your explanation of '{topic['title']}' is rated **{band}** ({score}/100).")

    if matched:
        names = ", ".join(m["label"] for m in matched)
        lines.append(f"You clearly covered: {names}.")

    if partial:
        names = ", ".join(p["label"] for p in partial)
        lines.append(f"You touched on {names} but didn't fully develop the idea — try to state it more explicitly and use precise terminology.")

    if missing:
        names = ", ".join(m["label"] for m in missing)
        lines.append(f"You missed: {names}. Consider revisiting these before your next attempt.")

    if misconceptions:
        lines.append("Also, a couple of statements suggest a misunderstanding:")
        for note in misconceptions:
            lines.append(f"  • {note}")

    if not missing and not misconceptions and not partial:
        lines.append("Strong, complete answer — you've demonstrated solid conceptual understanding.")

    return "\n".join(lines)
