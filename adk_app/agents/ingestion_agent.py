from typing import List
from pypdf import PdfReader
from adk_app.retrieval import chunk_text, Chunk
from adk_app.logging_utils import log_step
from adk_app.settings import settings

def ingest_pdfs(paths: List[str], logs: list[str]) -> List[Chunk]:
    all_chunks: List[Chunk] = []
    for idx, path in enumerate(paths):
        try:
            reader = PdfReader(path)
            log_step(logs, f'Loaded PDF {path} with {len(reader.pages)} pages')
            cnt = 0
            for p, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""
                if not text.strip():
                    log_step(logs, f'No extractable text on page {p} of {path} (possible scanned PDF)')
                    continue
                new = chunk_text(text, doc_id=f'doc{idx+1}', filename=path, page=p)
                all_chunks.extend(new)
                cnt += len(new)
                if cnt >= settings.max_chunks_per_doc:
                    log_step(logs, f'Max chunks reached for {path}; truncating')
                    break
        except Exception as e:
            log_step(logs, f'Failed to read {path}: {e}')
    log_step(logs, f'Chunked into {len(all_chunks)} passages total')
    return all_chunks
