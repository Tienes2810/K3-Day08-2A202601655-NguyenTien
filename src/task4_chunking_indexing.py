"""
Task 4 — Chunking & Indexing vào Vector Store (ChromaDB).

Chunking Strategy:
  - Legal documents: Hierarchical chunking (Chương → Điều → sub-chunk nếu dài)
  - News documents:  RecursiveCharacterTextSplitter (character-based)
"""

import re
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Configuration
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150
CHUNKING_METHOD = "hierarchical"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
VECTOR_STORE = "chromadb"
COLLECTION_NAME = "university_services_docs"

_model_cache = None


def get_embedding_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = SentenceTransformer(EMBEDDING_MODEL)
    return _model_cache


def get_collection():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def load_documents() -> list[dict]:
    """
    Đọc toàn bộ markdown files từ data/standardized/.
    """
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        doc_type = "legal" if "legal" in str(md_file.parent) else "news"
        documents.append({
            "content": content,
            "metadata": {
                "source": md_file.name,
                "type": doc_type
            }
        })
    return documents


# =============================================================================
# Hierarchical Chunking cho tài liệu pháp lý (Chương → Điều → sub-chunk)
# =============================================================================

def _detect_chuong(text: str) -> list[dict]:
    """
    Phát hiện và tách các Chương trong văn bản pháp lý.
    Trả về list of {'chuong': 'Chương I', 'title': 'NHỮNG QUY ĐỊNH CHUNG', 'content': ...}
    """
    # Pattern: "Chương I" hoặc "Chương VIII" etc, tiếp theo là tên chương trên dòng kế
    pattern = r'(Chương\s+[IVXLCDM]+)\s*\n+\s*([^\n]+)'
    splits = re.split(pattern, text)

    chuongs = []
    # Phần trước Chương đầu tiên (phần header/mở đầu)
    if splits[0].strip():
        chuongs.append({
            "chuong": "Phần mở đầu",
            "title": "",
            "content": splits[0].strip()
        })

    # Mỗi match tạo 3 groups: (text trước, Chương X, Tên chương, text sau)
    i = 1
    while i < len(splits) - 2:
        chuong_num = splits[i].strip()
        chuong_title = splits[i + 1].strip()
        chuong_content = splits[i + 2].strip() if i + 2 < len(splits) else ""
        chuongs.append({
            "chuong": chuong_num,
            "title": chuong_title,
            "content": chuong_content
        })
        i += 3

    # Nếu không phát hiện Chương nào → trả toàn bộ văn bản
    if not chuongs:
        chuongs.append({
            "chuong": "",
            "title": "",
            "content": text
        })

    return chuongs


def _detect_dieu(text: str) -> list[dict]:
    """
    Phát hiện và tách các Điều trong nội dung 1 Chương.
    Trả về list of {'dieu': 'Điều 7', 'title': 'Thời gian và tiến trình...', 'content': ...}
    """
    # Pattern: "Điều 7. Tên điều" hoặc "Điều 7:" etc
    pattern = r'(Điều\s+\d+)\s*[\.:\s]+\s*([^\n]+)'
    splits = re.split(pattern, text)

    dieus = []
    # Phần trước Điều đầu tiên
    if splits[0].strip():
        dieus.append({
            "dieu": "",
            "title": "",
            "content": splits[0].strip()
        })

    i = 1
    while i < len(splits) - 2:
        dieu_num = splits[i].strip()
        dieu_title = splits[i + 1].strip()
        dieu_content = splits[i + 2].strip() if i + 2 < len(splits) else ""
        # Gộp title + content
        full_content = f"{dieu_title}\n{dieu_content}".strip()
        dieus.append({
            "dieu": dieu_num,
            "title": dieu_title,
            "content": full_content
        })
        i += 3

    if not dieus:
        dieus.append({
            "dieu": "",
            "title": "",
            "content": text
        })

    return dieus


def _sub_chunk(text: str, max_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Sub-chunk text dài thành các phần nhỏ hơn max_size.
    Ưu tiên tách theo paragraph (\n\n), sau đó sentence (\n), cuối cùng theo ký tự.
    """
    if len(text) <= max_size:
        return [text]

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)
    except ImportError:
        # Simple fallback
        parts = []
        start = 0
        while start < len(text):
            end = start + max_size
            chunk_str = text[start:end].strip()
            if chunk_str:
                parts.append(chunk_str)
            start += (max_size - overlap)
        return parts


def _clean_page_headers(text: str) -> str:
    """Xóa các heading ## Page N do PDF converter tạo ra."""
    return re.sub(r'\n*## Page \d+\s*\n*', '\n', text)


def chunk_legal_document(doc: dict) -> list[dict]:
    """
    Hierarchical chunking cho tài liệu pháp lý:
    1. Tách theo Chương
    2. Trong mỗi Chương → tách theo Điều
    3. Nếu 1 Điều > CHUNK_SIZE → sub-chunk
    4. Gắn tiền tố [Chương X | Điều Y] vào đầu mỗi chunk
    """
    text = _clean_page_headers(doc["content"])
    chunks = []

    chuongs = _detect_chuong(text)

    for chuong in chuongs:
        chuong_label = chuong["chuong"]
        chuong_title = chuong["title"]
        chuong_prefix = f"{chuong_label} - {chuong_title}".strip(" -") if chuong_label else ""

        dieus = _detect_dieu(chuong["content"])

        for dieu in dieus:
            dieu_label = dieu["dieu"]
            dieu_title = dieu["title"]

            # Tạo prefix
            prefix_parts = []
            if chuong_prefix:
                prefix_parts.append(chuong_prefix)
            if dieu_label:
                prefix_parts.append(f"{dieu_label}. {dieu_title}")
            prefix = f"[{' | '.join(prefix_parts)}]\n" if prefix_parts else ""

            content = dieu["content"]

            # Sub-chunk nếu Điều quá dài
            # Trừ đi phần prefix để đảm bảo tổng không vượt max
            effective_max = CHUNK_SIZE - len(prefix)
            sub_chunks = _sub_chunk(content, max_size=max(effective_max, 400))

            for sub_idx, sub_text in enumerate(sub_chunks):
                full_content = f"{prefix}{sub_text}" if prefix else sub_text
                chunk_meta = {
                    **doc["metadata"],
                    "chunk_index": len(chunks),
                    "chuong": chuong_label,
                    "dieu": dieu_label,
                    "dieu_title": dieu_title,
                }
                chunks.append({
                    "content": full_content.strip(),
                    "metadata": chunk_meta
                })

    return chunks


def chunk_news_document(doc: dict) -> list[dict]:
    """Character-based chunking cho tài liệu tin tức (không có cấu trúc Chương/Điều)."""
    chunks = []
    sub_chunks = _sub_chunk(doc["content"], max_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

    for i, chunk_text in enumerate(sub_chunks):
        if chunk_text.strip():
            chunks.append({
                "content": chunk_text.strip(),
                "metadata": {
                    **doc["metadata"],
                    "chunk_index": i
                }
            })
    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents theo chiến lược phù hợp:
      - Legal: Hierarchical (Chương → Điều → sub-chunk)
      - News:  RecursiveCharacterTextSplitter
    """
    chunks = []
    for doc in documents:
        if doc["metadata"].get("type") == "legal":
            chunks.extend(chunk_legal_document(doc))
        else:
            chunks.extend(chunk_news_document(doc))
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed toàn bộ chunks bằng sentence-transformers.
    """
    if not chunks:
        return chunks

    model = get_embedding_model()
    texts = [c["content"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False)

    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb.tolist()

    return chunks


def index_to_vectorstore(chunks: list[dict]):
    """
    Lưu chunks vào ChromaDB.
    """
    if not chunks:
        return

    collection = get_collection()
    ids = [f"{c['metadata']['source']}_chunk_{c['metadata']['chunk_index']}_{i}" for i, c in enumerate(chunks)]
    documents = [c["content"] for c in chunks]
    embeddings = [c["embedding"] for c in chunks]
    # ChromaDB metadata chỉ chấp nhận str/int/float
    metadatas = []
    for c in chunks:
        meta = {}
        for k, v in c["metadata"].items():
            if isinstance(v, (str, int, float, bool)):
                meta[k] = v
        metadatas.append(meta)

    # ChromaDB upsert batching
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        collection.upsert(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )


def run_pipeline():
    """Chạy toàn bộ pipeline: load -> chunk -> embed -> index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing (Hierarchical)")
    print("=" * 50)

    docs = load_documents()
    print(f"[OK] Loaded {len(docs)} documents")

    legal_count = sum(1 for d in docs if d["metadata"]["type"] == "legal")
    news_count = sum(1 for d in docs if d["metadata"]["type"] == "news")
    print(f"  Legal: {legal_count} | News: {news_count}")

    chunks = chunk_documents(docs)
    print(f"[OK] Created {len(chunks)} chunks (hierarchical for legal, character for news)")

    # Hien thi thong ke
    legal_chunks = [c for c in chunks if c["metadata"].get("type") == "legal"]
    news_chunks = [c for c in chunks if c["metadata"].get("type") == "news"]
    print(f"  Legal chunks: {len(legal_chunks)} | News chunks: {len(news_chunks)}")

    if legal_chunks:
        dieu_set = set()
        for c in legal_chunks:
            d = c["metadata"].get("dieu", "")
            if d:
                dieu_set.add(f"{c['metadata']['source']}:{d}")
        print(f"  Unique Dieu detected: {len(dieu_set)}")

    chunks = embed_chunks(chunks)
    print(f"[OK] Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("[OK] Indexed to ChromaDB")


if __name__ == "__main__":
    run_pipeline()
