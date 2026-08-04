"""
RAG Chatbot — University Services (DUT - Bách khoa Đà Nẵng)
Streamlit app kết nối RAG Retrieval (Task 9) và Generation (Task 10).

Chạy:
    streamlit run app.py
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# PAGE CONFIG
st.set_page_config(
    page_title="DUT University Services RAG Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# SIDEBAR — INFO & SETTINGS
with st.sidebar:
    st.title("🎓 DUT RAG Chatbot")
    st.caption("Trợ lý hỏi đáp quy chế & dịch vụ sinh viên Trường Đại học Bách khoa - ĐH Đà Nẵng")

    st.divider()

    st.subheader("💡 Câu hỏi gợi ý")
    suggestions = [
        "Quy định về đồ án tốt nghiệp khóa 2021?",
        "Quy đổi chứng chỉ CNTT quốc tế như thế nào?",
        "Điều kiện xét học bổng khuyến khích học tập?",
        "Quy trình đăng ký học phần trên cổng SV DUT?",
        "Hướng dẫn dịch vụ thư viện và đặt phòng học nhóm?",
        "Quy định về liêm chính học thuật đối với sinh viên?",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True, key=f"sug_{hash(s)}"):
            st.session_state["pending_query"] = s

    st.divider()
    st.subheader("⚙️ Thiết lập")
    top_k = st.slider("Số chunks retrieval (top_k)", 3, 10, 5)

    st.divider()
    st.caption("**Kiến trúc hệ thống:**")
    st.caption("Hybrid Retrieval (Semantic + BM25) → RRF Rerank → PageIndex Fallback → LLM Generation có Citation")

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# MAIN CHAT AREA
st.title("🎓 DUT University Services RAG Chatbot")
st.caption("Hệ thống hỏi đáp thông tin chính sách & dịch vụ sinh viên (ĐH Bách khoa - ĐH Đà Nẵng)")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            with st.expander(f"📚 Nguồn tham khảo ({len(msg['sources'])} chunks)"):
                for i, src in enumerate(msg["sources"], 1):
                    meta = src.get("metadata", {})
                    source_name = meta.get("source", "Unknown")
                    doc_type = meta.get("type", "unknown")
                    cosine = src.get("original_cosine_score", src.get("score", 0))
                    rrf_score = src.get("score", 0)
                    st.markdown(f"**[{i}] {source_name}** `{doc_type}` | cosine: `{cosine:.4f}` | rrf: `{rrf_score:.4f}`")
                    st.text(src.get("content", "")[:300] + "...")
                    st.divider()

# QUERY HANDLING
user_input = st.chat_input("Nhập câu hỏi của bạn về chính sách/dịch vụ ĐH Bách khoa Đà Nẵng...")
query = user_input or st.session_state.pending_query

if query:
    st.session_state.pending_query = None

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang truy vấn dữ liệu DUT và tổng hợp câu trả lời..."):
            try:
                from src.task10_generation import generate_with_citation
                response = generate_with_citation(query, top_k=top_k)
                answer = response.get("answer", "Chưa thể trả lời.")
                sources = response.get("sources", [])
            except Exception as e:
                answer = f"❌ **Lỗi khi chạy RAG Pipeline:** {e}"
                sources = []

            st.markdown(answer)

            if sources:
                with st.expander(f"📚 Nguồn tham khảo ({len(sources)} chunks)"):
                    for i, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        source_name = meta.get("source", "Unknown")
                        doc_type = meta.get("type", "unknown")
                        cosine = src.get("original_cosine_score", src.get("score", 0))
                        rrf_score = src.get("score", 0)
                        st.markdown(f"**[{i}] {source_name}** `{doc_type}` | cosine: `{cosine:.4f}` | rrf: `{rrf_score:.4f}`")
                        st.text(src.get("content", "")[:300] + "...")
                        st.divider()

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
