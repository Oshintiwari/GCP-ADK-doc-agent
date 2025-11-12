from __future__ import annotations
from typing import List, Tuple
from pathlib import Path
from adk_app.utils import short_name

from adk_app.retrieval import Chunk, index_embeddings, search
from adk_app.logging_utils import log_step
from adk_app.settings import settings

# Prefer real Gemini clients; fall back to local stubs if import fails.
try:
    from adk_app.llm_clients import get_embedder, get_generator  # type: ignore
    _REAL_CLIENTS = True
except Exception:
    _REAL_CLIENTS = False

    def get_embedder():
        """
        Fallback stub: List[str] -> List[List[float]]
        Deterministic pseudo-embeddings for smoke tests without network/API.
        """
        import numpy as np

        def _fake_embed(batch: List[str]) -> List[List[float]]:
            out = []
            for t in batch:
                np.random.seed(abs(hash(t)) % (2**32))
                out.append(np.random.rand(768).tolist())
            return out

        return _fake_embed

    def get_generator():
        """
        Fallback stub with .generate(prompt) interface.
        """
        class _Stub:
            def generate(self, prompt: str) -> str:
                return "Placeholder answer (Gemini not wired yet)."
        return _Stub()

def answer_query(
    query: str,
    chunks: List[Chunk],
    logs: list[str],
    top_k: int | None = None
):
    if not chunks:
        log_step(logs, "No chunks available for retrieval")
        return "Not found in provided documents.", []

    # 1) Embed + index
    embedder = get_embedder()
    index_embeddings(chunks, embedder)

    # 2) Retrieve with optional override
    k = top_k if top_k is not None else settings.top_k
    results: List[Tuple[Chunk, float]] = search(query, chunks, embedder, k)
    log_step(logs, f"TopK retrieval returned {len(results)} passages")

    if not results:
        return "Not found in provided documents.", []

    # 3) Build grounded context + citations
    context_blocks: List[str] = []
    citations: List[dict] = []
    for c, score in results:
        context_blocks.append(f"[{short_name(c.filename)} p.{c.page}] {c.text}")
        citations.append({
            "doc_id": c.doc_id,
            "filename": short_name(c.filename),
            "page": c.page,
            "excerpt": c.text[:240],
        })
    context = "\n\n".join(context_blocks)

    # 4) Generate with strict grounding instructions
    generator = get_generator()
    prompt = (
        "You are a careful assistant. Answer using ONLY the provided context.\n"
        "If information conflicts across documents, note the differences and cite both.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Instructions:\n"
        "- Provide a concise answer (3–6 sentences).\n"
        "- Include inline citations like (filename p.X) where appropriate.\n"
        "- If not found in context, say 'Not found in provided documents.' and stop.\n"
    )

        # Support both real client (.generate) and accidental callable usage.
    answer = generator.generate(prompt) if hasattr(generator, "generate") else generator(prompt)

    # --- Post-process to guarantee at least one inline citation ---
    if "Not found in provided documents." not in answer and citations:
        has_inline_cite = ("(" in answer and " p." in answer)
        if not has_inline_cite:
            c0 = citations[0]
            fname = Path(c0["filename"]).name.replace("+", " ")
            answer = f"{answer} ({fname} p.{c0['page']})"
    # --------------------------------------------------------------

    return answer, citations



