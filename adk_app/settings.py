from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    # model names are placeholders; wired in Step 2
    embedding_model: str = "text-embedding-004"
    generation_model: str = "gemini-2.5-flash"
    chunk_chars: int = 1200
    chunk_overlap: int = 150
    top_k: int = 3
    max_chunks_per_doc: int = 1000

settings = Settings()
if not settings.google_api_key:
    print("WARNING: GOOGLE_API_KEY not set. Create .env from .env.example.")
