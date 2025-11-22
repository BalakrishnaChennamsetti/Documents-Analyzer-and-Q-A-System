# backend/ingest_pdf.py
import fitz  # PyMuPDF
from backend.vectordb import add_documents

def extract_pdf_pages(pdf_bytes):
    """Generator that yields text from each PDF page."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Failed to open PDF: {str(e)}")

    try:
        for page in doc:
            yield page.get_text("text")
    finally:
        doc.close()


def chunk_generator(text, chunk_size=100, overlap=20):
    """Yields chunks of text with optional overlap."""
    if not text:
        return

    length = len(text)
    start = 0

    while start < length:
        end = min(start + chunk_size, length)
        yield text[start:end]
        start = end - overlap if end - overlap > 0 else end


def insert_chunks_to_db(chunks, metadata, batch_size=2):
    """Inserts chunks into vector DB in batches."""
    batch = []
    for chunk in chunks:
        batch.append(chunk)
        if len(batch) >= batch_size:
            add_documents(
                texts=batch,
                metadatas=[metadata] * len(batch)
            )
            batch = []

    # Insert remaining
    if batch:
        add_documents(
            texts=batch,
            metadatas=[metadata] * len(batch)
        )


def ingest_pdf_file(file_bytes, metadata, chunk_size=100, overlap=20, batch_size=2):
    """Ingests a PDF file into the vector DB."""
    if not file_bytes:
        return {"status": "error", "message": "Empty PDF file"}

    total_chunks = 0

    try:
        for page_text in extract_pdf_pages(file_bytes):
            if not page_text.strip():
                continue
            chunks = chunk_generator(page_text, chunk_size=chunk_size, overlap=overlap)
            for chunk in chunks:
                try:
                    insert_chunks_to_db([chunk], metadata, batch_size=batch_size)
                    total_chunks += 1
                except MemoryError:
                    return {
                        "status": "error",
                        "message": "MemoryError: Chunk too large to process"
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Vector DB insert failed: {str(e)}"
                    }

    except Exception as e:
        return {"status": "error", "message": f"PDF processing failed: {str(e)}"}

    if total_chunks == 0:
        return {"status": "error", "message": "No valid text found in PDF"}

    return {
        "status": "pdf_ingested",
        "chunks": total_chunks,
        "metadata_added": True
    }
