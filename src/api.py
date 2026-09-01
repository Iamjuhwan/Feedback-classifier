"""
Step 4: demo API.

Serves the fine-tuned transformer classifier as the primary model, plus the
information extractor, behind one endpoint. The transformer loads directly
from the Hugging Face Hub (no large files needed in this repo):

  https://huggingface.co/Jesujuwon/community-health-feedback-afroxlmr

Falls back to the TF-IDF baseline (models/baseline_tfidf_logreg.joblib,
61.7% accuracy / 0.615 macro-F1) if the Hub model can't be reached (e.g. no
internet in a sandboxed environment).

Run: uvicorn api:app --reload
Then: POST /analyze  {"text": "..."}
"""

from pathlib import Path

import joblib
from fastapi import FastAPI
from pydantic import BaseModel

from extract import extract

REPO_ROOT = Path(__file__).resolve().parent.parent
HF_MODEL_ID = "Jesujuwon/community-health-feedback-afroxlmr"
BASELINE_PATH = REPO_ROOT / "models" / "baseline_tfidf_logreg.joblib"

app = FastAPI(title="Community Health Feedback Classifier")

_backend = None  # "transformer" | "baseline"
_transformer_pipeline = None
_baseline_model = None


def get_backend():
    """Lazy-load whichever model is available, preferring the Hub transformer."""
    global _backend, _transformer_pipeline, _baseline_model

    if _backend is not None:
        return _backend

    try:
        from transformers import pipeline
        _transformer_pipeline = pipeline(
            "text-classification",
            model=HF_MODEL_ID,
            tokenizer=HF_MODEL_ID,
            top_k=None,
        )
        _backend = "transformer"
    except Exception:
        _baseline_model = joblib.load(BASELINE_PATH)
        _backend = "baseline"

    return _backend


class FeedbackRequest(BaseModel):
    text: str


class FeedbackResponse(BaseModel):
    text: str
    predicted_label: str
    label_confidence: float
    model_backend: str
    extracted: dict


@app.post("/analyze", response_model=FeedbackResponse)
def analyze(req: FeedbackRequest):
    backend = get_backend()

    if backend == "transformer":
        results = _transformer_pipeline(req.text)[0]  # list of {label, score}
        best = max(results, key=lambda r: r["score"])
        pred, confidence = best["label"], float(best["score"])
    else:
        pred = _baseline_model.predict([req.text])[0]
        proba = _baseline_model.predict_proba([req.text])[0]
        confidence = float(max(proba))

    return FeedbackResponse(
        text=req.text,
        predicted_label=pred,
        label_confidence=round(confidence, 3),
        model_backend=backend,
        extracted=extract(req.text),
    )


@app.get("/health")
def health():
    return {"status": "ok", "model_backend": get_backend()}
