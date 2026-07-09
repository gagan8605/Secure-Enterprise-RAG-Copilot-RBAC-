"""
Central configuration for Secure Enterprise RAG Copilot.
All settings are read from environment variables (loaded from .env).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── LLM Settings ──────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# ─── JWT / Auth ────────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-dev-key-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

# ─── Storage Paths ─────────────────────────────────────────────────────────────
CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
DATA_PATH: str = os.getenv("DATA_PATH", "./data")
DB_PATH: str = os.getenv("DB_PATH", "./users.db")
COLLECTION_NAME: str = "enterprise_docs"

# ─── Embedding & Chunking ──────────────────────────────────────────────────────
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 50
TOP_K: int = 5

# Distance threshold — cosine distance above this = irrelevant chunk (filtered out)
RELEVANCE_THRESHOLD: float = 0.80

# ─── RBAC: Role → Allowed Access Levels ───────────────────────────────────────
# Higher roles have cumulative access (public ⊂ employee ⊂ manager ⊂ hr)
ROLE_ACCESS_MAP: dict[str, list[str]] = {
    "public":   ["public"],
    "employee": ["public", "employee"],
    "manager":  ["public", "employee", "manager"],
    "hr":       ["public", "employee", "manager", "hr"],
}

# Numeric level for display/comparison purposes
ROLE_LEVELS: dict[str, int] = {
    "public": 1,
    "employee": 2,
    "manager": 3,
    "hr": 4,
}

# All valid access levels (must match data/ subdirectory names)
ALL_ACCESS_LEVELS: list[str] = ["public", "employee", "manager", "hr"]
