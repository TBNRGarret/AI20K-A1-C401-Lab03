# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Đàm Lê Văn Toàn
- **Student ID**: 2A202600017
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**:
	- `Chatbot.py` (Baseline Chatbot không dùng tools)
	- `src/core/openai_provider.py` (nâng cấp kết nối OpenRouter + fallback key)

- **Code Highlights**:
	- Trong `Chatbot.py`, tôi xây dựng `SYSTEM_PROMPT` theo ngữ cảnh bán hàng E-commerce, đảm bảo bot trả lời tư vấn ngắn gọn và **không tự nhận đã kiểm tra kho/mã/ship** khi chưa có công cụ.
	- Trong `Chatbot.py`, hàm `build_chatbot()` nạp `.env`, lấy model mặc định `qwen/qwen3.6-plus:free`, kiểm tra API key và báo lỗi rõ ràng nếu thiếu key.
	- Trong `Chatbot.py`, vòng lặp `chat_loop()` cho phép chat liên tục, in thêm metadata (`latency`, `prompt_tokens`, `completion_tokens`, `total_tokens`) để phục vụ benchmark với Agent.
	- Trong `src/core/openai_provider.py`, tôi cập nhật cơ chế lấy key theo thứ tự ưu tiên `OPENROUTER_API_KEY` → `OPENAI_API_KEY`, đồng thời đặt `base_url` mặc định `https://openrouter.ai/api/v1` để dùng OpenRouter ổn định.
	- Trong `.env.example`, tôi thêm:
		- `OPENAI_MODEL=qwen/qwen3.6-plus:free`
		- `OPENROUTER_API_KEY=...`
		- `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1`

- **Documentation**:
	- Thành phần của tôi là **Baseline Chatbot** để làm mốc so sánh với ReAct Agent.
	- Luồng chạy: `User Input` → `Chatbot.py` → `OpenAIProvider.generate()` → OpenRouter/Qwen → trả lời trực tiếp.
	- Điểm khác với ReAct: Baseline **không có Thought-Action-Observation và không gọi tools**, nên dễ ảo giác hoặc trả lời thiếu chính xác ở các bài toán nhiều bước (giá + giảm giá + ship).

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**:
	- **Vấn đề nghiêm trọng**: Khi nâng cấp `Chatbot.py` từ chế độ `generate()` sang `stream()`, phần metadata (token counts: `prompt_tokens`, `completion_tokens`, `total_tokens`) bị **mất hoàn toàn**.
	- Nguyên nhân: OpenAI API trong chế độ streaming không trả về `response.usage` (chỉ có trong non-streaming), làm cho bản baseline không thể so sánh metrics với ReAct Agent sau này.
	- Ảnh hưởng: Mảng 5 (Telemetry Analyst) không có dữ liệu token để tính chi phí API và so sánh hiệu suất.

- **Log Source**:
	- Lỗi được phát hiện khi chạy `Chatbot.py` và so sánh output: phần `[meta]` không còn in `prompt_tokens`, `completion_tokens`, chỉ còn `latency` và `chars`.
	- Bằng chứng: code hiện tại chỉ in `f"[meta] latency={latency_ms}ms, chars={len(full_response)}\n"`, thiếu token metrics.

- **Diagnosis**:
	- **Root Cause**: OpenAI Python SDK không cấp `usage` object khi sử dụng streaming (vì server không biết khi nào stream kết thúc).
	- **Impact**: Baseline chatbot mà mảng 3 cung cấp không có token data, tạo điểm yếu khi benchmark với Agent (vốn có tool calls và có thể log từng bước).
	- **Trách nhiệm**: Đây là vấn đề thiết kế API, không phải lỗi implementation.

- **Solution**:
	- **Tạm thời**: Giữ vòng lặp stream nhưng thêm fallback logic: khi cần metrics, gọi `generate()` **song song** với `stream()` trên request đầu tiên, extract `usage`, rồi dùng số đó để normalize.
	- **Hoặc**: Thêm flag `--with-stats` để bạn chọn chế độ:
		- Default (stream): UX nhanh nhưng không có token.
		- `--with-stats`: Gọi `generate()` để có metrics, chậm hơn nhưng dữ liệu đầy đủ.
	- **Bình luận code**: Thêm comment trong `Chatbot.py` giải thích trade-off này cho mảng 5.
	- **Đề xuất cải tiến**: Phía mảng 1 (Agent Builder) nên tích hợp `logger` để ghi lại token data **trước** khi in, tránh phụ thuộc vào OpenAI's usage metadata.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?
2.  **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?
3.  **Observation**: How did the environment feedback (observations) influence the next steps?

- **Reasoning**:
	- Với baseline chatbot, mô hình trả lời trực tiếp từ ngôn ngữ tự nhiên nên không có cơ chế tách bài toán thành các bước kiểm chứng.
	- Với ReAct, `Thought` giúp agent lập kế hoạch rõ ràng: kiểm tra tồn kho/giá → áp mã giảm giá → tính ship → tổng hợp kết quả, nhờ đó giảm trả lời cảm tính.

- **Reliability**:
	- Agent có thể tệ hơn chatbot khi parser Action chưa ổn hoặc mô hình xuất sai định dạng (ví dụ sai tên tool, sai tham số), dẫn đến lặp hoặc fail call.
	- Chatbot đôi khi cho câu trả lời trôi chảy hơn về mặt ngôn ngữ, nhưng độ chính xác nghiệp vụ lại thấp hơn khi cần tính toán đa bước.

- **Observation**:
	- Observation là tín hiệu phản hồi quan trọng để agent sửa hướng suy luận ngay lập tức.
	- Ví dụ khi tool báo “không tìm thấy sản phẩm”, agent có thể đổi sang hỏi rõ tên sản phẩm thay vì tiếp tục tính toán trên dữ liệu giả định.
	- Điều này tạo khác biệt lớn so với chatbot baseline vốn không có vòng phản hồi từ môi trường.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**:
	- Tách lớp model gateway riêng (OpenAI/OpenRouter/Gemini) + retry/backoff + timeout chuẩn hóa.
	- Dùng hàng đợi bất đồng bộ cho tool calls để xử lý đồng thời nhiều phiên chat.

- **Safety**:
	- Thêm policy guardrails để chặn tool arguments bất hợp lệ (số âm, kiểu dữ liệu sai, mã độc).
	- Bổ sung lớp xác thực kết quả (validator) trước khi trả “Final Answer” cho người dùng.

- **Performance**:
	- Cache kết quả tool có tính lặp cao (ví dụ giá/tồn kho ít thay đổi theo phiên ngắn).
	- Theo dõi token/latency theo từng request để tối ưu prompt và chọn model phù hợp tải hệ thống.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
