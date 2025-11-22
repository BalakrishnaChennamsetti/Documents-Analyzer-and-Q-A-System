# backend/rag_query.py
from fastapi import FastAPI
from pydantic import BaseModel
from backend.vectordb import similarity_search
from backend.web_search import web_search
import uvicorn
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    docs = similarity_search(q, top_k=k, metadata_filter=metadata_filter)

    if not docs or len(docs) == 0:
        web = web_search(q)
        return {"answer": None, "source": "web", "web": web}
    print([d for d in [docs]])
    docs = docs["documents"]
    flat_docs = [d[0] for d in docs]
    combined = "\n\n".join(flat_docs)
    short = combined[:3000]
    return {"answer": short, "source": "vector_db", "docs": docs}

if __name__ == "__main__":
    uvicorn.run("backend.rag_query:app", host="0.0.0.0", port=8002, reload=True)
