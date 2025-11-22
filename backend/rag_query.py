# backend/rag_query.py
from fastapi import FastAPI
from pydantic import BaseModel
from backend.vectordb import similarity_search
from backend.web_search import web_search
import uvicorn

app = FastAPI(title="RAG Query API")

class QueryIn(BaseModel):
    query: str
    k: int = 5
    sentiment_filter: str = None  # optional: "POSITIVE"/"NEGATIVE"

@app.post("/query")
async def query_endpoint(qin: QueryIn):
    q = qin.query
    k = qin.k

    metadata_filter = None
    if qin.sentiment_filter:
        metadata_filter = {"sentiment": qin.sentiment_filter}

    docs = similarity_search(q, k=k, metadata_filter=metadata_filter)

    if not docs or len(docs) == 0:
        web = web_search(q)
        return {"answer": None, "source": "web", "web": web}

    combined = "\n\n".join([d["text"] for d in docs])
    short = combined[:3000]
    return {"answer": short, "source": "vector_db", "docs": docs}

if __name__ == "__main__":
    uvicorn.run("backend.rag_query:app", host="0.0.0.0", port=8002, reload=True)
