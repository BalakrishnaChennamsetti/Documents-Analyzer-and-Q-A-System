# backend/process_webhook.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.ingest_text import ingest_transcript
from backend.ingest_pdf import ingest_pdf_file
from backend.ingest_csv import ingest_csv_file
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ingest & RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest")
async def ingest(file: UploadFile = File(...), label: str = Form(None)):
    filename = file.filename
    filetype = filename.split(".")[-1].lower()
    contents = await file.read()
    metadata = {"filename": filename, "label": label}
    logger.info(f"Received file: {filename} of type: {filetype} with label: {label}")

    if filetype == "txt":
        text = contents.decode("utf-8", errors="ignore")
        res = ingest_transcript(text, metadata)
        logger.info(f"Ingested text file: {filename} with result: {res}")
        return {"status": "ok", "type": "txt", "result": res}


    elif filetype == "pdf":
        res = ingest_pdf_file(contents, metadata)
        logger.info(f"Ingested PDF file: {filename} with result: {res}")
        return {"status": "ok", "type": "pdf", "result": res}

    elif filetype == "csv":
        res = ingest_csv_file(contents, metadata)
        logger.info(f"Ingested CSV file: {filename} with result: {res}")
        return {"status": "ok", "type": "csv", "result": res}

    else:
        logger.warning(f"Unsupported file type: {filetype} for file: {filename}")
        return {"status": "error", "reason": "unsupported filetype"}

if __name__ == "__main__":
    uvicorn.run("backend.process_webhook:app", host="0.0.0.0", port=8001, reload=True)
