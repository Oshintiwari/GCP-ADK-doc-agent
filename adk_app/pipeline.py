import time
from typing import List

from adk_app.schemas import QAResponse, Meta, Citation
from adk_app.settings import settings
from adk_app.logging_utils import log_step
from adk_app.agents.ingestion_agent import ingest_pdfs
from adk_app.agents.reasoning_agent import answer_query


def run_pipeline(pdf_paths: List[str], query: str, top_k: int | None = None) -> QAResponse:
    """
    Orchestrates ingestion -> retrieval -> generation.
    - pdf_paths: list of absolute or relative PDF file paths
    - query: natural language question
    - top_k: optional override for retrieval depth (defaults to settings.top_k)
    """
    logs: list[str] = []
    t0 = time.time()
    log_step(logs, f'Start pipeline with {len(pdf_paths)} PDFs; query="{query}"')

    # 1) Ingest PDFs -> chunks
    chunks = ingest_pdfs(pdf_paths, logs)

    # 2) Retrieve + Generate
    chosen_k = top_k if top_k is not None else settings.top_k
    answer, cites_raw = answer_query(query, chunks, logs, top_k=chosen_k)

    # 3) Build response
    latency_ms = int((time.time() - t0) * 1000)
    citations = [Citation(**c) for c in cites_raw]
    confidence = min(1.0, len(citations) / max(1, chosen_k))

    resp = QAResponse(
        query=query,
        answer=answer or "Not found in provided documents.",
        citations=citations,
        meta=Meta(
            used_model=settings.generation_model,
            num_docs=len(pdf_paths),
            retrieval_k=chosen_k,
            latency_ms=latency_ms,
            tokens_input=0,
            tokens_output=0,
            confidence=confidence,
        ),
        logs=logs,
    )
    return resp
