"""
Quick-start helper script.
Run this once after setting up .env to verify everything is configured correctly.

    python quickstart.py
"""
import sys
import os
from pathlib import Path

# Avoid UnicodeEncodeError on Windows console when printing emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")



def check(label: str, ok: bool, detail: str = ""):
    mark = "✅" if ok else "❌"
    msg = f"  {mark}  {label}"
    if detail:
        msg += f"  →  {detail}"
    print(msg)
    return ok


def main():
    print("\n" + "=" * 60)
    print("  🔐 Secure Enterprise RAG Copilot — Pre-flight Check")
    print("=" * 60 + "\n")

    all_ok = True

    # 1. Python version
    py_ok = sys.version_info >= (3, 10)
    all_ok &= check("Python 3.10+", py_ok, f"Running {sys.version.split()[0]}")

    # 2. .env file
    env_path = Path(".env")
    env_ok = env_path.exists()
    all_ok &= check(".env file exists", env_ok,
                    "Found" if env_ok else "Run: copy .env.example .env  then fill in GROQ_API_KEY")

    if env_ok:
        from dotenv import load_dotenv
        load_dotenv()
        groq_key = os.getenv("GROQ_API_KEY", "")
        key_ok = groq_key and not groq_key.startswith("gsk_your")
        all_ok &= check("GROQ_API_KEY set", key_ok,
                        "OK" if key_ok else "Edit .env and paste your Groq API key from console.groq.com")

    # 3. Data directories
    for level in ["public", "employee", "manager", "hr"]:
        d = Path(f"data/{level}")
        d_ok = d.exists() and any(d.iterdir())
        all_ok &= check(f"data/{level}/ has files", d_ok,
                        f"{len(list(d.iterdir()))} file(s)" if d.exists() else "Directory missing")

    # 4. Core packages
    for pkg in ["fastapi", "chromadb", "groq", "streamlit", "sentence_transformers"]:
        try:
            __import__(pkg.replace("-", "_"))
            check(f"Package: {pkg}", True)
        except ImportError:
            check(f"Package: {pkg}", False, "Run: pip install -r requirements.txt")
            all_ok = False

    print()
    if all_ok:
        print("  🎉 All checks passed! You're ready to go.\n")
        print("  Next steps:")
        print("  1. python -m backend.ingest          ← build the vector store")
        print("  2. uvicorn backend.main:app --reload  ← start the API (port 8000)")
        print("  3. streamlit run frontend/app.py      ← start the UI  (port 8501)")
        print()
        print("  Or with Docker:")
        print("  docker-compose up --build")
        print("  docker exec rag-backend python -m backend.ingest")
    else:
        print("  ⚠️  Some checks failed — fix the issues above before running.\n")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
