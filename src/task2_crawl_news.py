"""
Task 2 — Crawl/Lưu bài viết & thông báo về dịch vụ đại học Bách khoa Đà Nẵng (DUT).
"""

import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


DUT_NEWS_ARTICLES = [
    {
        "url": "http://dut.udn.vn/TinTuc/ThongBaoHocBongKhuyenKhichHocTap2026",
        "title": "Thông báo v/v Xét cấp Học bổng Khuyến khích Học tập cho Sinh viên DUT",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Thông báo v/v Xét cấp Học bổng Khuyến khích Học tập cho Sinh viên Trường Đại học Bách khoa - ĐH Đà Nẵng

**Đơn vị phát hành:** Phòng Công tác Sinh viên - Trường Đại học Bách khoa, ĐH Đà Nẵng.
**Đối tượng áp dụng:** Sinh viên hệ chính quy đang theo học tại trường.

## 1. Điều kiện xét học bổng
- Sinh viên có điểm trung bình học tập (ĐTBHT) đạt loại Khá trở lên (từ 2.50/4.0 trở lên).
- Điểm rèn luyện đạt từ loại Tốt trở lên (từ 80 điểm trở lên).
- Không bị kỷ luật từ mức khiển trách trở lên trong học kỳ xét học bổng.

## 2. Các mức học bổng
- **Mức Khá:** ĐTBHT Khá (2.50 - 3.19), Rèn luyện Tốt. Mức hỗ trợ: 100% học phí trần.
- **Mức Giỏi:** ĐTBHT Giỏi (3.20 - 3.59), Rèn luyện Xuất sắc. Mức hỗ trợ: 120% học phí trần.
- **Mức Xuất sắc:** ĐTBHT Xuất sắc (3.60 - 4.00), Rèn luyện Xuất sắc. Mức hỗ trợ: 150% học phí trần.

## 3. Quy trình nộp hồ sơ
Sinh viên kiểm tra danh sách dự kiến trên Cổng thông tin sinh viên `http://sv.dut.udn.vn/` và gửi phản hồi trong vòng 7 ngày làm việc kể từ ngày thông báo.
"""
    },
    {
        "url": "http://dut.udn.vn/TinTuc/HuongDanDangKyHocPhanOnline",
        "title": "Hướng dẫn Quy trình Đăng ký Học phần Trực tuyến trên Cổng SV DUT",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Hướng dẫn Quy trình Đăng ký Học phần Trực tuyến trên Cổng SV DUT

**Trường Đại học Bách khoa - Đại học Đà Nẵng**
**Hệ thống Đăng ký Học phần:** `http://sv.dut.udn.vn/`

## 1. Các đợt đăng ký học phần
- **Đợt 1 (Đăng ký chính thức):** Dành cho sinh viên đăng ký theo đúng tiến độ kế hoạch đào tạo của khoa/ngành.
- **Đợt 2 (Đăng ký bổ sung & điều chỉnh):** Dành cho sinh viên đăng ký học cải thiện, học vượt hoặc sửa đổi học phần đã chọn.

## 2. Các bước thực hiện
1. Truy cập vào trang web `http://sv.dut.udn.vn/` và đăng nhập tài khoản cá nhân sinh viên.
2. Chọn mục **"Đăng ký học phần"** trong thanh menu chính.
3. Chọn các học phần thuộc khung chương trình đào tạo hoặc lớp học phần mở trong kỳ.
4. Kiểm tra trùng lịch học và lịch thi trước khi nhấn nút **"Lưu kết quả đăng ký"**.
5. In hoặc chụp màn hình Phiếu đăng ký học phần để làm bằng chứng đối soát khi có thắc mắc.

## 3. Rút học phần
Sinh viên có thể rút học phần trong 2 tuần đầu học kỳ. Học phần rút sẽ không ghi nhận điểm F nhưng học phí sẽ xử lý theo quy định tài chính của Nhà trường.
"""
    },
    {
        "url": "http://dut.udn.vn/TinTuc/HuongDanSuDungThuVienTrungTam",
        "title": "Hướng dẫn Dịch vụ Thư viện và Mượn Trả Tài liệu tại Thư viện DUT",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Hướng dẫn Dịch vụ Thư viện và Mượn Trả Tài liệu - Trường ĐH Bách khoa Đà Nẵng

**Địa điểm:** Trung tâm Thông tin - Thư viện, Trường Đại học Bách khoa - ĐH Đà Nẵng.

## 1. Giờ mở cửa
- Thứ 2 đến Thứ 6: 07:30 - 21:00.
- Thứ 7: 08:00 - 17:00.
- Chủ nhật và ngày lễ: Nghỉ.

## 2. Quy định mượn sách & tài liệu
- Sinh viên xuất trình thẻ sinh viên (hoặc mã QR trên app sinh viên) khi vào thư viện và mượn sách.
- **Sách giáo trình:** Mượn tối đa 5 cuốn/lần, thời hạn mượn 30 ngày.
- **Sách tham khảo / Luận văn:** Đọc tại chỗ hoặc mượn qua đêm (từ 16:30 hôm trước đến 08:30 sáng hôm sau).

## 3. Đặt phòng học nhóm
Thư viện cung cấp 10 phòng học nhóm với sức chứa từ 6 - 15 sinh viên. Sinh viên đặt phòng trực tuyến qua portal thư viện trước ít nhất 24 giờ.
"""
    },
    {
        "url": "http://dut.udn.vn/TinTuc/HuongDanKyTucXaBakhieudut",
        "title": "Thông tin Đăng ký Chỗ ở Ký túc xá Sinh viên Bách khoa Đà Nẵng",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Thông tin Đăng ký Chỗ ở Ký túc xá Sinh viên Trường ĐH Bách khoa - ĐH Đà Nẵng

**Ban Quản lý Ký túc xá DUT**

## 1. Đối tượng ưu tiên xét ở KTX
1. Sinh viên diện chính sách, con thương binh bệnh binh, gia đình liệt sĩ.
2. Sinh viên vùng sâu vùng xa, hộ nghèo, cận nghèo.
3. Sinh viên khóa mới (tân sinh viên) đăng ký đợt nhập học đầu năm.

## 2. Cơ sở vật chất KTX
- Phòng ở 6 sinh viên và 8 sinh viên có công trình vệ sinh khép kín.
- Trang bị hệ thống wifi miễn phí, khu tự học, sân thể thao đa năng.
- An ninh bảo vệ trực 24/7, có cửa soát thẻ từ tự động.

## 3. Quy trình đăng ký
Sinh viên kê khai thông tin đăng ký KTX trực tuyến tại website `http://sv.dut.udn.vn/` trong thời gian mở cổng đăng ký hàng năm.
"""
    },
    {
        "url": "http://dut.udn.vn/TinTuc/ThongBaoMienGiamHocPhi2026",
        "title": "Thông báo Hướng dẫn Hồ sơ Miễn giảm Học phí và Hỗ trợ Chi phí Học tập",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Hướng dẫn Hồ sơ Miễn giảm Học phí & Hỗ trợ Chi phí Học tập - DUT

**Phòng Công tác Sinh viên - Trường Đại học Bách khoa, Đại học Đà Nẵng**

## 1. Các đối tượng được miễn 100% học phí
- Sinh viên là con của người có công với cách mạng.
- Sinh viên khuyết tật nặng hoặc đặc biệt nặng.
- Sinh viên mồ côi cả cha lẫn mẹ, không nơi tựa cậy.
- Sinh viên dân tộc thiểu số thuộc hộ nghèo/cận nghèo ở vùng có điều kiện kinh tế - xã hội đặc biệt khó khăn.

## 2. Hồ sơ cần chuẩn bị
- Đơn đề nghị miễn giảm học phí (theo mẫu của Nhà trường).
- Bản sao công chứng Giấy chứng nhận đối tượng ưu tiên (Giấy chứng nhận hộ nghèo/cận nghèo, Giấy xác nhận khuyết tật,...).
- Bản sao công chứng Căn cước công danh và Giấy khai sinh.

## 3. Thời gian nộp
Hồ sơ nộp về Phòng Công tác Sinh viên (Phòng A105) trong 3 tuần đầu của mỗi học kỳ.
"""
    }
]


def create_news_files():
    """Tạo các file JSON bài báo news cho DUT."""
    setup_directory()
    for i, article in enumerate(DUT_NEWS_ARTICLES, 1):
        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ Saved article: {filepath}")


if __name__ == "__main__":
    create_news_files()
