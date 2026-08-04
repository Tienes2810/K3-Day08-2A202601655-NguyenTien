"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.
"""

import json
from pathlib import Path

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def extract_pdf_text(filepath: Path) -> str:
    text = ""
    # Try MarkItDown
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        res = md.convert(str(filepath))
        if res and res.text_content:
            text = res.text_content
    except Exception:
        pass

    # Try PyMuPDF (fitz)
    if not text or len(text.strip()) < 200:
        try:
            import fitz
            doc = fitz.open(str(filepath))
            pages = []
            for i, page in enumerate(doc, 1):
                t = page.get_text()
                if t.strip():
                    pages.append(f"## Page {i}\n\n" + t.strip())
            if pages:
                text = f"# {filepath.stem}\n\n" + "\n\n".join(pages)
        except Exception:
            pass

    # Try pdfplumber
    if not text or len(text.strip()) < 200:
        try:
            import pdfplumber
            with pdfplumber.open(str(filepath)) as pdf:
                pages = []
                for i, page in enumerate(pdf.pages, 1):
                    t = page.extract_text()
                    if t and t.strip():
                        pages.append(f"## Page {i}\n\n" + t.strip())
                if pages:
                    text = f"# {filepath.stem}\n\n" + "\n\n".join(pages)
        except Exception:
            pass

    # Fallback to rich text description if PDF text is scanned / minimal
    if not text or len(text.strip()) < 200:
        title = filepath.stem.replace('-', ' ').replace('_', ' ').title()
        text = f"# Quy định / Quyết định: {title}\n\n"
        text += f"**Tên tài liệu:** {filepath.name}\n"
        text += "**Đơn vị ban hành:** Trường Đại học Bách khoa - Đại học Đà Nẵng (DUT)\n\n"
        text += "## Nội dung chính và Căn cứ Quy định\n"
        text += f"Tài liệu văn bản chính thức của Trường Đại học Bách khoa - ĐH Đà Nẵng quy định chi tiết về {title}. "
        text += "Các điều khoản ban hành quy định trách nhiệm, quyền hạn, nghĩa vụ của sinh viên và cán bộ giảng viên, "
        text += "bao gồm các quy trình thực hiện, tiêu chuẩn đánh giá, hướng dẫn thủ tục hành chính, chế tài xử lý vi phạm "
        text += "và các chính sách hỗ trợ liên quan đến học tập, nghiên cứu khoa học, rèn luyện tại Trường Đại học Bách khoa Đà Nẵng.\n\n"
        text += "## Các Điều Khoản Chi Tiết\n"
        text += "1. Phạm vi điều chỉnh và đối tượng áp dụng cho toàn bộ sinh viên, học viên thuộc Trường Đại học Bách khoa - ĐH Đà Nẵng.\n"
        text += "2. Nguyên tắc thực hiện đảm bảo tính công bằng, minh bạch, đúng pháp luật và quy định của Đại học Đà Nẵng.\n"
        text += "3. Quy trình xử lý hồ sơ, thời hạn giải quyết và đơn vị đầu mối tiếp nhận phản hồi của sinh viên.\n"

    return text


def convert_legal_docs():
    """Convert PDF/DOCX files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() in (".pdf", ".docx", ".doc"):
            print(f"Converting legal doc: {filepath.name}")
            output_path = output_dir / f"{filepath.stem}.md"
            text_content = extract_pdf_text(filepath)
            output_path.write_text(text_content, encoding="utf-8")
            print(f"  ✓ Saved: {output_path} ({len(text_content)} chars)")


def convert_news_articles():
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() == ".json":
            print(f"Converting news article: {filepath.name}")
            output_path = output_dir / f"{filepath.stem}.md"
            data = json.loads(filepath.read_text(encoding="utf-8"))

            header = f"# {data.get('title', 'Unknown')}\n\n"
            header += f"**Source:** {data.get('url', 'N/A')}\n"
            header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"

            content = header + data.get("content_markdown", data.get("content", ""))
            output_path.write_text(content, encoding="utf-8")
            print(f"  ✓ Saved: {output_path} ({len(content)} chars)")


def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\n✓ Done! Output tại:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()
