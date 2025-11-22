# backend/sentiment.py
from transformers import pipeline

# lazy-init pipeline
_pipe = None

def _get_pipeline():
    global _pipe
    if _pipe is None:
        _pipe = pipeline("sentiment-analysis")
    return _pipe

def analyze_sentiment(text: str) -> str:
    snippet = text[:4000]  # limit to reasonable length
    pipe = _get_pipeline()
    res = pipe(snippet)
    if isinstance(res, list) and len(res) > 0:
        label = res[0].get("label", "UNKNOWN")
        return label
    return "UNKNOWN"
