# ─── Stage 1: Build ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for sentence-transformers, chromadb, pypdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ─── Stage 2: Runtime ───────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/   ./backend/
COPY frontend/  ./frontend/
COPY tests/     ./tests/
COPY data/      ./data/

# Create directories
RUN mkdir -p chroma_db

# Environment (override at runtime with docker run -e or docker-compose)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHROMA_DB_PATH=/app/chroma_db \
    DATA_PATH=/app/data

EXPOSE 8000

# Default: run FastAPI backend
# Override for frontend: docker run ... streamlit run frontend/app.py
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
