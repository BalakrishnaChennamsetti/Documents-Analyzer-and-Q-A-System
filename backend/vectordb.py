# backend/vectordb.py

from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

# -----------------------------------------------------------------------------
# LAZY LOAD EMBEDDING MODEL (prevents FastAPI reload multiprocessing crashes)
# -----------------------------------------------------------------------------

_embedding_model = None

def get_model():
    """
    Load the embedding model only once (lazy load)
    Avoids reloading during FastAPI hot reload (important!)
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


# -----------------------------------------------------------------------------
# CHROMA DB CLIENT (new API v0.5+)
# -----------------------------------------------------------------------------

client = PersistentClient(path="./chroma_db")

# Create or get collection
collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # cosine distance is best for embeddings
)


# -----------------------------------------------------------------------------
# ADD MULTIPLE DOCUMENTS
# -----------------------------------------------------------------------------

def add_documents(texts, metadatas):
    """
    Add multiple text chunks to the vector DB.
    - texts: list[str]
    - metadatas: list[dict]
    """
    if len(texts) == 0:
        return {"status": "no_texts"}

    model = get_model()
    embeddings = model.encode(texts).tolist()

    ids = [f"doc_{i}" for i in range(len(texts))]

    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return {"status": "added", "count": len(texts)}


# -----------------------------------------------------------------------------
# ADD/SAVE A SINGLE CHUNK OR TEXT (used by ingest_text.py)
# -----------------------------------------------------------------------------

def store_vector(text, metadata):
    """
    Store a single text chunk with metadata and embedding.
    Used for transcript storage.
    """
    model = get_model()
    embedding = model.encode([text]).tolist()

    collection.add(
        ids=[metadata.get("id", "auto_id")],
        documents=[text],
        metadatas=[metadata],
        embeddings=embedding
    )

    return {"status": "stored", "id": metadata.get("id", "auto_id")}


# -----------------------------------------------------------------------------
# QUERY THE VECTOR DB
# -----------------------------------------------------------------------------

def query_vector(query_text, top_k=3):
    """
    Query vector DB to retrieve top_k similar chunks.
    Returns matching text + metadata.
    """
    model = get_model()
    embedding = model.encode([query_text]).tolist()[0]

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    return results


# -----------------------------------------------------------------------------
# DELETE ENTIRE COLLECTION (optional utility)
# -----------------------------------------------------------------------------

def clear_database():
    """
    Optional utility to clear all data.
    Useful during dev/testing.
    """
    client.delete_collection(name="documents")
    return {"status": "cleared"}
