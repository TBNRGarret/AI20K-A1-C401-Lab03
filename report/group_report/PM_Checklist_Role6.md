# Bảng Kế Hoạch & Checklist: Vai Trò 6 (Project Manager / Technical Writer)

Bảng công việc này được thiết kế theo lộ trình thực hiện bài Lab (Topic: Smart E-commerce Agent). Bạn hãy đánh dấu (x) vào các ô vuông `[ ]` khi hoàn thành để theo dõi tiến độ.

---

## 📅 Giai đoạn 1: Chuẩn bị & Khởi động
- [x] **Họp Kick-off:** Tổ chức họp nhóm chốt đề tài "Smart E-commerce Agent" (Agent Check tồn kho + Xử lý mã giảm giá + Tính ship).
- [x] **Phân vai:** Giao nhiệm vụ cụ thể cho cả 6 thành viên dựa trên outline bạn đã có. Đảm bảo ai cũng biết cần phải sinh ra output gì.
- [x] **Lập môi trường:** Tạo Git Repository / Thư mục Google Drive chung để mọi người gom mã nguồn (source code) và file log.
- [x] **Chốt mốc thời gian (Milestones):** Đặt hạn chót (deadline) nộp Code (Agent v1), nộp kết quả Test (Logs), và hạn chót nộp báo cáo thô.

## 🧩 Giai đoạn 2: Theo dõi & Giục bài (Thời gian Code)
- [x] **[Giục Mảng 2 - Tools]:** Bắt bạn Dev này cam kết thiết kế cấu trúc JSON thật chuẩn cho 3 tools (`check_inventory`, `get_discount`, `calc_shipping`). Lưu lại mô tả (description) để lát nhét vào báo cáo nhóm. -> Đã code tại [`src/tools/tools.py`](../../src/tools/tools.py)
- [x] **[Giục Mảng 3 - Setup API]:** Đảm bảo bạn này đã dựng xong `Baseline_Chatbot.py` (Phiên bản trợ lý siêu ngố không có kết nối Tool) cấu hình API xong xuôi. -> Tham khảo [`Chatbot.py`](../../Chatbot.py) và [`src/core/openai_provider.py`](../../src/core/openai_provider.py)
- [x] **[Giục Mảng 1 - Theo dõi ReAct]:** Yêu cầu quay màn hình hoặc ném vài cái log chứng minh Agent suy luận `Thought -> Action -> Observation` thành công. -> **ĐÃ XONG:** Agent v1 chạy mượt trên Gemini (Xem log test ngày 06/04).
- [x] **[Giục Mảng 4 - Thu thập Dữ liệu Test]:** Bắt bạn QA cung cấp 1 bảng so sánh: Đưa 1 câu hỏi E-commerce phức tạp cho Chatbot (trả lời láo) và đưa cho ReAct Agent (trả lời chuẩn xác nhờ chạy Tool). -> **ĐÃ XONG:** Dữ liệu đã được lấy từ [`tests/test_local.py`](../../tests/test_local.py)
- [ ] **[Giục Mảng 5 - Quét Log]:** Báo bạn đọc Log tìm ra cho bạn ít nhất 1 cái lỗi hoàn hảo (VD: Agent gọi nhầm tham số, rơi vào vòng lặp... để làm mồi viết báo cáo). Thu thập số Token, Tốc độ.

## ✍️ Giai đoạn 3: Viết Báo Cáo Nhóm (Group Report) - Nồi Cơm Của Bạn
- [ ] Đổi tên file `TEMPLATE_GROUP_REPORT.md` thành `GROUP_REPORT_[Ten_Nhom].md`.
- [ ] **Mục 1 (Executive Summary):** Tóm tắt dự án E-commerce, khẳng định tỷ lệ giải quyết thành công các câu hỏi của Agent so với Chatbot thường.
- [ ] **Mục 2.1 (ReAct Loop):** Vẽ một Flowchart (Dùng Mermaid/Draw.io) trình bày cách 1 request mua hàng được bộ não Agent xử lý như thế nào. Trực quan thì ăn điểm mạnh.
- [ ] **Mục 2.2 (Tool Definitions):** Bỏ bảng mô tả 3 tool do bạn Mảng 2 đưa vào đây.
- [ ] **Mục 3 (Telemetry):** Update số liệu Latency, Token Rate, Tiền API do Mảng 5 cung cấp.
- [ ] **Mục 4 & 5 (Root Cause Analysis & Ablation):** Trình bày cái Log lỗi mà Mảng 5 gom được. Cách nhóm phát hiện Agent "khù khờ", và do Mảng 1 sửa Prompt như thế nào đã giúp Agent sáng dạ lên (Agent v1 -> v2).
- [ ] **Mục 6 (Production Readiness):** Ghi rõ thiết kế dự kiến mang Agent này ra thương mại hoá (Thêm cơ chế Guardrail để Bot không giảm giá 100%, bảo mật dòng tiền...).

## 🎓 Giai đoạn 4: Báo cáo cá nhân & Chốt Đơn Đóng Gói
- [ ] Gửi "tối hậu thư" cho 5 thành viên còn lại: Yêu cầu nộp file `[TenThanhVien]_individual_report.md` theo format. Không nộp điểm 0 phần cá nhân ráng chịu.
- [ ] Đọc lướt 5 báo cáo của mọi người, kiểm tra có đúng tiêu chí "Phân tích 1 Case Study Lỗi" chưa. Hỗ trợ mọi người sửa nếu viết sơ sài.
- [ ] **Tự viết Báo Cáo Cá Nhân của Role 6:** Liệt kê công việc PM, Quản trị rủi ro log (Failure Analysis), và đề xuất "Scale (mở rộng) hệ thống lên Multi-Agent (1 bot Sales + 1 bot Customer Service)".
- [ ] Kiểm tra lại thư mục `report/`. Nén lại (ZIP/Push code) và vinh quang nộp bài!
