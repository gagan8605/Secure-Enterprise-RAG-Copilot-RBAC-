"""
SQLite user store — initializes DB, seeds demo users, provides lookup helpers.
Passwords are hashed with bcrypt via passlib.
"""
import sys
import sqlite3
from pathlib import Path
from passlib.context import CryptContext

# Avoid UnicodeEncodeError on Windows console when printing emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from backend.config import DB_PATH

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# ─── Demo users seeded on first startup ────────────────────────────────────────
DEMO_USERS = [
    ("alice",  "alice123",  "public"),
    ("bob",    "bob123",    "employee"),
    ("carol",  "carol123",  "manager"),
    ("dave",   "dave123",   "hr"),
]


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create users table and seed demo accounts (idempotent)."""
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            role          TEXT    NOT NULL
                              CHECK(role IN ('public','employee','manager','hr'))
        )
    """)
    conn.commit()

    for username, password, role in DEMO_USERS:
        exists = cur.execute(
            "SELECT id FROM users WHERE username=?", (username,)
        ).fetchone()
        if not exists:
            hashed = pwd_context.hash(password)
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                (username, hashed, role),
            )

    conn.commit()
    conn.close()
    print("✅ Users DB ready — demo accounts: alice/bob/carol/dave")


def get_user(username: str) -> dict | None:
    """Return user row as dict, or None if not found."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=?", (username,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


if __name__ == "__main__":
    init_db()
