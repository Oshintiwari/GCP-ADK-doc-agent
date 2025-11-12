from typing import List, Tuple
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from adk_app.settings import settings
# 🔽 NEW: lightweight disk cache for embeddings
from adk_app.cache import get_cached, put_cached, flush


@dataclass
class Chunk:
    doc_id: str
    filename: str
    page: int
    text: str
    embedding: np.ndarray | None = None


def chunk_text(text: str, doc_id: str, filename: str, page: int) -> List[Chunk]:
    chunks: List[Chunk] = []
    step = max(1, settings.chunk_chars - settings.chunk_overlap)
    for i in range(0, len(text), step):
        piece = text[i:i+settings.chunk_chars]
        if piece.strip():
            chunks.append(Chunk(doc_id=doc_id, filename=filename, page=page, text=piece))
    return chunks


def embed_texts(embedder_callable, texts: List[str]) -> np.ndarray:
    # embedder_callable: List[str] -> List[List[float]]
    vecs = embedder_callable(texts)
    return np.array(vecs, dtype=np.float32)


def index_embeddings(chunks: List[Chunk], embedder_callable) -> None:
    """
    Populate chunk.embeddings in-place, using cache when available.
    Only calls the embedder for texts that are not cached yet.
    """
    if not chunks:
        return

    to_embed_texts: List[str] = []
    to_embed_idx: List[int] = []

    # 1) Try cache for each chunk
    for i, c in enumerate(chunks):
        if c.embedding is not None:
            continue
        cached = get_cached(c.text, settings.embedding_model)
        if cached is not None:
            c.embedding = np.array(cached, dtype=np.float32)
        else:
            to_embed_texts.append(c.text)
            to_embed_idx.append(i)

    # 2) Embed only the misses
    if to_embed_texts:
        vecs = embed_texts(embedder_callable, to_embed_texts)
        for idx, vec in zip(to_embed_idx, vecs):
            chunks[idx].embedding = vec
            # persist to cache (as list for JSON)
            put_cached(chunks[idx].text, settings.embedding_model, vec.tolist())
        flush()  # write cache to disk once per batch


def search(query: str, all_chunks: List[Chunk], embedder_callable, top_k: int) -> List[Tuple[Chunk, float]]:
    if not all_chunks:
        return []

    # 🔽 Cache the query embedding too
    q_cached = get_cached(query, settings.embedding_model)
    if q_cached is not None:
        qv = np.array(q_cached, dtype=np.float32).reshape(1, -1)
    else:
        qv = embed_texts(embedder_callable, [query])[0].reshape(1, -1)
        put_cached(query, settings.embedding_model, qv.flatten().tolist())
        flush()

    mats = [c.embedding for c in all_chunks if c.embedding is not None]
    if not mats:
        return []

    mat = np.vstack(mats)
    sims = cosine_similarity(qv, mat)[0]
    ranked = list(zip([c for c in all_chunks if c.embedding is not None], sims))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
