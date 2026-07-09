"""
Document ingestion pipeline for Secure Enterprise RAG Copilot.

Walks data/<access_level>/ directories, loads PDF/MD/TXT files,
chunks them, embeds with sentence-transformers, and stores in ChromaDB
with access_level metadata for RBAC filtering at query time.

Run from project root:
    python -m backend.ingest
"""
import sys
import os
from pathlib import Path

# Ensure project root is on sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

# Avoid UnicodeEncodeError on Windows console when printing emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

from backend.config import (
    CHROMA_DB_PATH,
    DATA_PATH,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    ALL_ACCESS_LEVELS,
)


# ─── Supported file types ──────────────────────────────────────────────────────
LOADERS = {
    ".pdf": PyPDFLoader,
    ".txt": lambda p: TextLoader(p, encoding="utf-8"),
    ".text": lambda p: TextLoader(p, encoding="utf-8"),
    ".md": lambda p: TextLoader(p, encoding="utf-8"),   # plain-text MD
}


def _get_loader(file_path: Path):
    ext = file_path.suffix.lower()
    factory = LOADERS.get(ext)
    if factory is None:
        return None
    try:
        return factory(str(file_path))
    except Exception as e:
        print(f"    ⚠️  Could not create loader for {file_path.name}: {e}")
        return None


def ingest_documents(reset: bool = True) -> int:
    """
    Main ingestion entry-point.

    Parameters
    ----------
    reset : bool
        If True (default), delete the existing ChromaDB collection before
        ingesting. Set to False to append to an existing collection.

    Returns
    -------
    int : total number of chunks stored.
    """
    print("\n" + "=" * 60)
    print("  🚀  Secure Enterprise RAG — Document Ingestion")
    print("=" * 60)

    # ── Embedding model ────────────────────────────────────────────────────────
    print(f"\n📦  Loading embedding model: {EMBEDDING_MODEL}")
    print("    (first run downloads ~80 MB — please wait)\n")
    embeddings_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # ── ChromaDB client ────────────────────────────────────────────────────────
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"🗑️   Deleted existing collection '{COLLECTION_NAME}'")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # ── Text splitter ──────────────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    total_chunks = 0

    # ── Walk data/<access_level>/ directories ──────────────────────────────────
    for level in ALL_ACCESS_LEVELS:
        level_dir = Path(DATA_PATH) / level
        if not level_dir.exists():
            print(f"⚠️   Directory not found, skipping: {level_dir}")
            continue

        files = [f for f in level_dir.iterdir() if f.is_file()]
        print(f"📁  [{level.upper():8s}] — {len(files)} file(s)")

        for fp in files:
            loader = _get_loader(fp)
            if loader is None:
                print(f"    ⏭️   Skipped (unsupported type): {fp.name}")
                continue

            try:
                docs = loader.load()
            except Exception as e:
                print(f"    ❌  Load error for {fp.name}: {e}")
                continue

            chunks = splitter.split_documents(docs)
            if not chunks:
                print(f"    ⚠️   No chunks produced: {fp.name}")
                continue

            # Build ChromaDB batch
            ids, documents, metadatas = [], [], []
            for idx, chunk in enumerate(chunks):
                cid = f"{level}__{fp.stem}__{idx:04d}"
                ids.append(cid)
                documents.append(chunk.page_content)
                metadatas.append(
                    {
                        "access_level": level,
                        "source_file": fp.name,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                    }
                )

            # Embed
            vectors = embeddings_model.embed_documents(documents)

            # Store
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=vectors,
                metadatas=metadatas,
            )

            total_chunks += len(chunks)
            print(f"    ✅  {fp.name:<40s} → {len(chunks):3d} chunks  [{level}]")

    print(f"\n{'=' * 60}")
    print(f"  ✨  Ingestion complete!")
    print(f"  📊  Total chunks in ChromaDB : {collection.count()}")
    print(f"  🔢  This run added           : {total_chunks} chunks")
    print(f"{'=' * 60}\n")
    return total_chunks


if __name__ == "__main__":
    ingest_documents()
