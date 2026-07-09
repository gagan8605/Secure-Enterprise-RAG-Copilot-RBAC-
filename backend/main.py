"""
FastAPI application for Secure Enterprise RAG Copilot.

Endpoints:
  POST /login   — authenticate and receive JWT
  GET  /me      — return current user info
  POST /ask     — RBAC-filtered RAG query (requires Bearer token)
  GET  /health  — liveness probe

Run with:
    uvicorn backend.main:app --reload --port 8000
"""
import sys
import logging
from datetime import timedelta

# Avoid UnicodeEncodeError on Windows console when printing emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import authenticate_user, create_access_token, get_current_user
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES
from backend.database import init_db
from backend.models import (
    AskRequest,
    AskResponse,
    LoginRequest,
    SourceChunk,
    Token,
    UserInfo,
)
from backend.retriever import retrieve_and_answer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ─── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Secure Enterprise RAG Copilot",
    description=(
        "A document Q&A API with Role-Based Access Control enforced at the retrieval layer. "
        "Users only ever see LLM answers derived from chunks they are permitted to access."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow Streamlit frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    init_db()
    logger.info("✅ Secure Enterprise RAG Copilot API is ready")


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """Liveness probe — returns 200 if the API is running."""
    return {"status": "healthy", "service": "Secure Enterprise RAG Copilot"}


@app.post("/login", response_model=Token, tags=["Auth"])
async def login(request: LoginRequest):
    """
    Authenticate with username + password.
    Returns a signed JWT containing the user's role.
    """
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    logger.info("Login: user=%s role=%s", user["username"], user["role"])
    return Token(
        access_token=token,
        token_type="bearer",
        role=user["role"],
        username=user["username"],
    )


@app.get("/me", response_model=UserInfo, tags=["Auth"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's username and role."""
    return UserInfo(username=current_user["username"], role=current_user["role"])


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
async def ask(
    request: AskRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Submit a question. The system retrieves only documents within the
    authenticated user's permission level, then answers via the LLM.

    - `answer`          : LLM-generated answer (or access-denied message)
    - `sources`         : retrieved chunks shown for transparency
    - `chunks_retrieved`: number of permitted chunks found
    - `access_denied`   : true if no permitted chunks were found
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    username = current_user["username"]
    role = current_user["role"]

    logger.info("Ask: user=%s role=%s question='%s'", username, role, question[:80])

    result = retrieve_and_answer(question, role)

    return AskResponse(
        answer=result["answer"],
        sources=[SourceChunk(**s) for s in result["sources"]],
        query=question,
        user_role=role,
        chunks_retrieved=result["chunks_retrieved"],
        access_denied=result.get("access_denied", False),
    )


# ─── Dev entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
