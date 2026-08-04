"""
Task 10 — Generation Có Citation.
"""

import os
from dotenv import load_dotenv
from .task9_retrieval_pipeline import retrieve

load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3
LLM_MODEL = "openai/gpt-4o-mini"

# Ngưỡng cosine tối thiểu để chấp nhận context là đủ tin cậy
MIN_EVIDENCE_SCORE = 0.2

SYSTEM_PROMPT = """Bạn là trợ lý trả lời câu hỏi về dịch vụ và chính sách của Trường Đại học Bách khoa - Đại học Đà Nẵng (DUT)
(học phí, học bổng, ký túc xá, thư viện, đăng ký học phần, liêm chính học thuật, quy chế đào tạo).

Quy tắc BẮT BUỘC (TUYỆT ĐỐI TUÂN THỦ):
1. CHỈ sử dụng thông tin từ context được cung cấp — KHÔNG bịa đặt, KHÔNG suy luận ngoài context.
2. Mỗi khẳng định phải có trích dẫn nguồn ngay phía sau, ví dụ: [qd209-quy-dinh-do-an-tot-nghiep.md].
3. Nếu câu hỏi KHÔNG liên quan đến DUT hoặc context không chứa thông tin liên quan → BẮT BUỘC trả lời ĐÚNG câu sau: "Xin lỗi, câu hỏi này nằm ngoài phạm vi thông tin về Trường ĐH Bách khoa - ĐH Đà Nẵng mà tôi có thể hỗ trợ."
4. KHÔNG trả lời các câu hỏi về thời tiết, tin tức chung, toán học, lập trình, giải trí, hay bất kỳ chủ đề nào không liên quan đến dịch vụ/chính sách DUT — kể cả khi context có chứa từ khóa tương tự.
5. Trả lời bằng tiếng Việt, có cấu trúc rõ ràng theo các đoạn văn.
6. Không suy luận hay mở rộng ngoài những gì được nêu trong context."""

OUT_OF_SCOPE_ANSWER = "Xin lỗi, câu hỏi này nằm ngoài phạm vi thông tin về Trường ĐH Bách khoa - ĐH Đà Nẵng mà tôi có thể hỗ trợ."
NO_EVIDENCE_ANSWER = "Tôi không thể xác minh thông tin này từ nguồn hiện có về Trường ĐH Bách khoa - ĐH Đà Nẵng."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks để tránh "lost in the middle" effect.
    Input order:  [1, 2, 3, 4, 5]
    Output order: [1, 3, 5, 4, 2]
    """
    if len(chunks) <= 2:
        return chunks

    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """
    Format chunks thành context string cho prompt.
    Mỗi chunk có label source để LLM trích dẫn.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("metadata", {}).get("source", f"Source_{i}")
        doc_type = chunk.get("metadata", {}).get("type", "unknown")
        context_parts.append(
            f"[Document {i} | Source: {source} | Type: {doc_type}]\n"
            f"{chunk['content']}\n"
        )
    return "\n---\n".join(context_parts)


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end RAG generation có citation.
    """
    if not query:
        return {
            "answer": "Vui lòng nhập câu hỏi của bạn.",
            "sources": [],
            "retrieval_source": "none"
        }

    chunks = retrieve(query, top_k=top_k)

    # Guard 1: Không có kết quả nào → ngoài phạm vi
    if not chunks:
        return {
            "answer": OUT_OF_SCOPE_ANSWER,
            "sources": [],
            "retrieval_source": "none"
        }

    # Guard 2: Best cosine score quá thấp → evidence không đáng tin cậy
    best_cosine = max(
        (c.get("original_cosine_score", c.get("score", 0)) for c in chunks),
        default=0
    )
    if best_cosine < MIN_EVIDENCE_SCORE:
        return {
            "answer": NO_EVIDENCE_ANSWER,
            "sources": [],
            "retrieval_source": "none"
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    answer = ""

    if api_key:
        try:
            from openai import OpenAI
            base_url = "https://openrouter.ai/api/v1" if os.getenv("OPENROUTER_API_KEY") else None
            client = OpenAI(api_key=api_key, base_url=base_url)

            user_message = f"Context:\n{context}\n\n---\n\nQuestion: {query}"
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"LLM API Call Exception: {e}")

    # Robust local synthesis fallback if LLM API is unavailable/unconfigured
    if not answer:
        sources_summary = []
        for c in chunks[:3]:
            src_name = c.get("metadata", {}).get("source", "Tài liệu DUT")
            snippet = c["content"][:200].replace('\n', ' ')
            sources_summary.append(f"Theo **[{src_name}]**: {snippet}...")

        answer = f"Dựa trên tài liệu quy định của Trường ĐH Bách khoa - ĐH Đà Nẵng:\n\n" + "\n\n".join(sources_summary)

    retrieval_src = chunks[0].get("source", "hybrid") if chunks else "none"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_src
    }


if __name__ == "__main__":
    test_queries = [
        "Quy định về đồ án tốt nghiệp bách khoa?",
        "Thời tiết hôm nay thế nào?",
        "Who is the president of the USA?",
    ]
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = generate_with_citation(q)
        print(f"A: {result['answer'][:200]}")
        print(f"[Sources: {len(result['sources'])} | via {result['retrieval_source']}]")
