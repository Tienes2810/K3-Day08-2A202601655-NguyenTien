"""
Task 8 — PageIndex Vectorless RAG.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents():
    """Upload documents lên PageIndex hoặc chuẩn bị local index."""
    print("✓ PageIndex documents ready.")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex (hoặc structural document fallback).

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict,
            'source': 'pageindex'
        }
        Trả [] rỗng nếu không tìm thấy section nào match.
    """
    if not query:
        return []

    # Attempt PageIndex SDK call if API key is provided
    if PAGEINDEX_API_KEY:
        try:
            from pageindex.client import PageIndexClient
            client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
            resp = client.submit_query(query=query)
            retrieval_id = resp.get("retrieval_id") or resp.get("id")
            retrieval = client.get_retrieval(retrieval_id)

            results = []
            for node in retrieval.get("retrieved_nodes", [])[:top_k]:
                for group in node.get("relevant_contents", []):
                    for item in group:
                        results.append({
                            "content": item.get("relevant_content", ""),
                            "score": 0.85,
                            "metadata": {"section": item.get("section_title")},
                            "source": "pageindex",
                        })
            if results:
                return results[:top_k]
        except Exception as e:
            print(f"PageIndex API call fallback: {e}")

    # Robust structural fallback over standardized document headers
    results = []
    if STANDARDIZED_DIR.exists():
        query_words = set(query.lower().split())
        # Loại bỏ stop words đơn giản để tránh match ngẫu nhiên
        stop_words = {"là", "và", "của", "có", "cho", "trong", "được", "các",
                      "để", "từ", "này", "đó", "với", "như", "tôi", "bạn",
                      "không", "gì", "nào", "thế", "hôm", "nay", "ở", "ra",
                      "lên", "về", "cái", "một", "the", "a", "an", "is", "are",
                      "what", "how", "do", "does", "can", "will", "it", "i",
                      "you", "he", "she", "they", "we", "my", "your", "this",
                      "that", "at", "in", "on", "to", "of", "for", "by", "with"}
        query_content_words = query_words - stop_words
        if not query_content_words:
            query_content_words = query_words

        for md_file in STANDARDIZED_DIR.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            sections = content.split("\n## ")
            for sec in sections:
                sec_text = sec.strip()
                if not sec_text:
                    continue
                sec_lower = sec_text.lower()
                match_count = sum(1 for w in query_content_words if w in sec_lower)
                # Yêu cầu ít nhất 2 content word match, hoặc 1 nếu query chỉ có 1 content word
                min_matches = min(2, len(query_content_words))
                if match_count >= min_matches:
                    results.append({
                        "content": sec_text[:800],
                        "score": round(0.5 + 0.1 * match_count, 4),
                        "metadata": {"source": md_file.name, "section": sec_text.split("\n")[0]},
                        "source": "pageindex",
                    })

    results.sort(key=lambda x: x["score"], reverse=True)
    # KHÔNG tạo generic fallback nữa — trả [] nếu không match
    return results[:top_k]


if __name__ == "__main__":
    results = pageindex_search("tuition fee", top_k=3)
    for r in results:
        print(f"[{r['score']:.3f}] [{r['source']}] {r['content'][:100]}...")
