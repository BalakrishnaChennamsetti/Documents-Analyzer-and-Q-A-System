from backend.vectordb import store_vector
from backend.sentiment import analyze_sentiment


def ingest_transcript(text):

    # Step 1: Sentiment Analysis
    sentiment = analyze_sentiment(text)

    metadata = {
        "type": "transcript",
        "sentiment": sentiment
    }

    # Step 2: Store in Vector DB
    store_vector(text, metadata)

    return {
        "status": "success",
        "message": "Transcript ingested with sentiment tagging",
        "sentiment": sentiment
    }
