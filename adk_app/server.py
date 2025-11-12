from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from adk_app.pipeline import run_pipeline
from adk_app.schemas import QAResponse

app = FastAPI(title="ADK Doc Agent", version="0.1.0")


class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = None          # override retrieval K (optional)
    data_dir: str = "data"               # where PDFs live (default ./data)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=QAResponse)
def ask(req: AskRequest):
    pdf_dir = Path(req.data_dir)
    if not pdf_dir.exists():
        raise HTTPException(status_code=400, detail=f"data_dir not found: {pdf_dir}")

    pdfs: List[str] = [str(p) for p in sorted(pdf_dir.glob("*.pdf"))]
    if not pdfs:
        raise HTTPException(status_code=400, detail=f"No PDFs found in {pdf_dir}")

    # run the pipeline (uses your settings + optional top_k override)
    resp = run_pipeline(pdf_paths=pdfs, query=req.question, top_k=req.top_k)
    # FastAPI can return Pydantic models directly, but we’ll be explicit:
    return resp
