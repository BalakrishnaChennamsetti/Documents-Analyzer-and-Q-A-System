# backend/gemini_summarizer.py
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def call_gemini(text: str):
    """
    Placeholder stub for Gemini API call.
    Replace URL and payload with real Gemini API spec when you have it.
    """
    if not GEMINI_KEY:
        return None
    url = "https://api.gemini.example/v1/summarize"  # <-- replace"
    headers = {"Authorization": f"Bearer {GEMINI_KEY}"}
    payload = {"text": text}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json().get("summary")
    except Exception:
        return None
    return None

def local_extractive_summary(text: str, top_n: int = 5) -> str:
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if len(sentences) <= top_n:
        return '. '.join(sentences)
    vect = TfidfVectorizer(stop_words='english')
    X = vect.fit_transform(sentences)
    scores = np.array(X.sum(axis=1)).ravel()
    top_idx = np.argsort(scores)[-top_n:][::-1]
    summary = '. '.join([sentences[i] for i in top_idx])
    return summary

def summarize_with_gemini_or_local(text: str) -> str:
    g = call_gemini(text)
    if g:
        return g
    return local_extractive_summary(text)
