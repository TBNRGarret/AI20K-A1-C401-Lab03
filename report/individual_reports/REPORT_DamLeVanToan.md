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
	- **Vấn đề nghiêm trọng**: Trong `src/core/openai_provider.py`, hàm `generate()` **không kiểm tra `None`** trước khi truy cập `response.usage.prompt_tokens`.
	- Khi OpenRouter API trả về `response.usage = None` (xảy ra với một số model hoặc khi API bị throttle/error), code sẽ **crash ngay** với:
		```
		AttributeError: 'NoneType' object has no attribute 'prompt_tokens'
		```
	- Điều này làm toàn bộ chatbot dừng hoạt động, chứ không graceful fallback.

- **Log Source**:
	- Lỗi được nhận diện khi chạy `python Chatbot.py` với OpenRouter API và gọi hàm `chatbot.generate()`.
	- Stack trace:
		```python
		File "src/core/openai_provider.py", line 36, in generate
		    "prompt_tokens": response.usage.prompt_tokens,
		AttributeError: 'NoneType' object has no attribute 'prompt_tokens'
		```

- **Diagnosis**:
	- **Root Cause**: Lập trình viên giả định `response.usage` luôn tồn tại, nhưng thực tế OpenRouter/OpenAI API có thể trả `None` trong các trường hợp edge (model không hỗ trợ usage tracking, API quota exceeded, hoặc malformed response).
	- **Ảnh hưởng**: Baseline Chatbot trở thành unreliable, không thể so sánh công bằng với ReAct Agent. Mảng 4 (QA) sẽ gặp lỗi trong test.
	- **Tầng độc**: Lỗi này nằm ở tầng provider (provider layer), không phải application logic.

- **Solution**:
	- Thêm defensive check trong `src/core/openai_provider.py`:
		```python
		usage = {
		    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
		    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
		    "total_tokens": response.usage.total_tokens if response.usage else 0
		}
		```

	- **Logging**: Ghi warning khi usage là None để mảng 5 biết không có data cho request đó.
	- **Test case**: Thêm unit test trong `tests/` để mock API response với `usage=None` và kiểm tra chatbot xử lý gracefully.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?
2.  **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?
3.  **Observation**: How did the environment feedback (observations) influence the next steps?

- **Kết quả chạy Baseline Chatbot (No Agent)**:
```bash
(rag) vantoan@vantoan:~/VSCode/assignments/Day-3-Lab-Chatbot-vs-react-agent/AI20K-A1-C401-Lab03$ python Chatbot.py 
=== Baseline Chatbot (No Tools) ===
Model: qwen/qwen3.6-plus:free
Nhập 'exit' để thoát.

Bạn: toi muon mua 1 cai iphone 15, hay tu van va cho toi xem nhung ma giam gia toi co the ap dung
Bot: Chào bạn! Rất vui được hỗ trợ bạn chọn mua iPhone 15 nhé. 

📱 **Tư vấn nhanh:** iPhone 15 hiện có 3 mức dung lượng (128GB, 256GB, 512GB) và 5 màu (Đen, Xanh, Hồng, Vàng, Xanh dương). Máy đã nâng cấp camera chính 48MP, chip A16 Bionic, cổng USB-C và pin dùng bền hơn đời trước. Bạn thường ưu tiên dung lượng lưu trữ, màu sắc hay ngân sách cụ thể để mình gợi ý phiên bản phù hợp nhất?

⚠️ **Lưu ý quan trọng:** Hiện mình không có quyền truy cập trực tiếp vào kho, bảng giá hay mã giảm giá cập nhật theo thời gian thực của các sàn/nhà phân phối. Để mình hỗ trợ tính toán giá cuối cùng và hướng dẫn áp dụng khuyến mãi chính xác, bạn vui lòng nhắn mình thêm 3 thông tin:
1. Bạn dự định mua trên sàn/web nào? (Shopee, Lazada, Tiki, FPT, CelluS, Web Apple, v.v.)
2. Dung lượng & màu sắc bạn chọn?
3. Tỉnh/thành phố nhận hàng (để mình đối chiếu chính sách ship nếu sàn có công khai)?

Ngay khi có thông tin, mình sẽ tổng hợp các nhóm mã giảm giá phổ biến thường áp dụng cho iPhone 15 (voucher sàn, giảm cho thành viên, Freeship/Xtra, quà tặng kèm) và hướng dẫn bạn thao tác áp dụng + chốt đơn nhanh nhất. Bạn nhắn thêm thông tin nhé! 💙
[meta] latency=24105ms, prompt=127, completion=1060, total=1187

Bạn: exit
Tạm biệt!
```

- **Nhận xét từ kết quả baseline**:
	- Bot trả lời tự nhiên, lịch sự, nhưng không thể đưa ra con số chốt đơn chính xác vì không có quyền gọi tool kiểm kho/mã giảm giá/ship.
	- `latency=24105ms` và `completion=1060` cho thấy câu trả lời khá dài, chi phí token cao dù chưa giải được bài toán tính giá cuối cùng.
	- Đây là bằng chứng phù hợp để đối chiếu với ReAct Agent: cần vòng lặp Tool-Calling để chuyển từ “tư vấn chung” sang “tính toán chính xác”.

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

