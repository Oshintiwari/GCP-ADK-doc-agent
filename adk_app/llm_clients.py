from __future__ import annotations
import os
from typing import List, Callable

from adk_app.settings import settings

# Try ADK first; if not available, use google-generativeai directly.
_USE_ADK = False
try:
    import google_adk  # noqa: F401
    from google_adk.embeddings import gemini as adk_embeddings
    from google_adk.llms import gemini as adk_llms
    _USE_ADK = True
except Exception:
    _USE_ADK = False

def get_embedder() -> Callable[[List[str]], List[List[float]]]:
    if _USE_ADK:
        emb = adk_embeddings.Embedding(model=settings.embedding_model)
        return emb.embed

    import google.generativeai as genai
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY missing for embedding client")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def _embed(batch: List[str]) -> List[List[float]]:
        # try one batched call
        try:
            resp = genai.embed_content(model=settings.embedding_model, content=batch)
            # newer SDK returns {'embeddings': [{'embedding': [...]}, ...]} for batches
            if isinstance(resp, dict) and "embeddings" in resp:
                return [e["embedding"] for e in resp["embeddings"]]
            # some versions return {'embedding': [...]} even for singletons
            if isinstance(resp, dict) and "embedding" in resp:
                return [resp["embedding"]]
        except Exception:
            pass  # fall back to per-item below

        # fallback: per-item (slower but reliable)
        out = []
        for t in batch:
            r = genai.embed_content(model=settings.embedding_model, content=t)
            out.append(r["embedding"])
        return out

    return _embed

def get_generator():
    """
    Returns a simple object with a .generate(prompt=...) -> str interface
    """
    if _USE_ADK:
        model = adk_llms.GenerativeModel(model=settings.generation_model)
        class _ADKGen:
            def generate(self, prompt: str) -> str:
                out = model.generate(prompt=prompt)
                return getattr(out, "text", str(out))
        return _ADKGen()

    # Fallback to google-generativeai
    import google.generativeai as genai
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY missing for generator client")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(settings.generation_model)
    class _GenAI:
        def generate(self, prompt: str) -> str:
            out = model.generate_content(prompt)
            # `out.text` is typical; fallback to str if needed
            return getattr(out, "text", str(out))
    return _GenAI()
