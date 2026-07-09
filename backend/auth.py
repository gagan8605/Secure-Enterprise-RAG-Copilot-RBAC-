"""
JWT authentication helpers for Secure Enterprise RAG Copilot.

- create_access_token  : signs a JWT with username + role
- authenticate_user    : validates credentials against the SQLite DB
- get_current_user     : FastAPI dependency that verifies Bearer token
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.database import get_user, verify_password

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Return user dict on success, None on failure."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency.
    Decodes the Bearer JWT and returns {"username": ..., "role": ...}.
    Raises 401 on any failure.
    """
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if not username or not role:
            raise invalid
        return {"username": username, "role": role}
    except JWTError:
        raise invalid
