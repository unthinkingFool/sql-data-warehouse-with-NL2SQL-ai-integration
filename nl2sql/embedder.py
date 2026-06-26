
"""
RAG Indexer: Embeds the warehouse schema into a local vector store.
Run once (or when schema changes): python -m nl2sql.embedder
"""

import os
import re
from pathlib import Path
from typing import List

import chromadb
from sentence_transformers import SentenceTransformer


SCHEMA_FILE = Path(__file__).parent.parent / "docs" / "schema_context.md"
CHROMA_DIR  = Path(__file__).parent.parent / ".chroma_db"
COLLECTION  = "warehouse_schema"


def split_schema_into_chunks(text: str) -> List[dict]:
    """
    Splits schema_context.md into semantic chunks.
    Each chunk = one table section (from ## heading to the next).
    Returns list of dicts with 'id', 'text', and 'metadata'.
    """
    chunks = []
    
    # Split on level-2 headings (## table_name)
    sections = re.split(r'\n(?=## )', text)
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        
        # Extract table name from heading
        lines = section.strip().split('\n')
        heading = lines[0].strip('#').strip() if lines else f"section_{i}"
        
        # Further split large sections into sub-chunks (columns vs business rules vs examples)
        sub_sections = re.split(r'\n\*\*(?:Business rules|Sample business|Common Multi)', section)
        
        for j, sub in enumerate(sub_sections):
            if len(sub.strip()) < 50:  # skip tiny fragments
                continue
            
            chunk_id = f"{heading.lower().replace(' ', '_')}_{j}"
            chunks.append({
                "id": chunk_id,
                "text": sub.strip(),
                "metadata": {
                    "table": heading,
                    "section_index": i,
                    "chunk_index": j,
                    "source": "schema_context.md"
                }
            })
    
    return chunks


def build_index(force_rebuild: bool = False) -> chromadb.Collection:
    """
    Builds (or loads) the ChromaDB vector index from schema_context.md.
    
    Args:
        force_rebuild: If True, drops and rebuilds the collection.
    
    Returns:
        The ChromaDB collection ready for querying.
    """
    CHROMA_DIR.mkdir(exist_ok=True)
    
    # Initialize ChromaDB client (persistent — survives restarts)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # Check if we already have a collection
    existing_collections = [c.name for c in client.list_collections()]
    
    if COLLECTION in existing_collections and not force_rebuild:
        print(f"[Embedder] Loading existing index '{COLLECTION}' from {CHROMA_DIR}")
        return client.get_collection(name=COLLECTION)
    
    # Delete old collection if rebuilding
    if COLLECTION in existing_collections:
        client.delete_collection(name=COLLECTION)
        print(f"[Embedder] Dropped old collection '{COLLECTION}'")
    
    # Load and chunk schema document
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_FILE}\n"
            "Please create docs/schema_context.md first."
        )
    
    schema_text = SCHEMA_FILE.read_text(encoding="utf-8")
    chunks = split_schema_into_chunks(schema_text)
    print(f"[Embedder] Split schema into {len(chunks)} chunks")
    
    # Load embedding model (runs locally, no API cost)
    # all-MiniLM-L6-v2: fast, good for technical text, ~80MB download
    print("[Embedder] Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Embed all chunks
    texts = [c["text"] for c in chunks]
    ids   = [c["id"] for c in chunks]
    metas = [c["metadata"] for c in chunks]
    
    print(f"[Embedder] Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()
    
    # Store in ChromaDB
    collection = client.create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"}  # cosine similarity
    )
    
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metas
    )
    
    print(f"[Embedder] Index built. {len(chunks)} chunks stored in {CHROMA_DIR}")
    return collection


if __name__ == "__main__":
    build_index(force_rebuild=True)
    print("[Embedder] Done. Run app.py to start the query interface.")