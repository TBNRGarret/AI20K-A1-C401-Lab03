# Test Cases — Smart E-commerce Agent (QA & Prompt Attack)
**Member 4 | Role: QA & Prompt Attacker**  
**Branch:** `feature/qa-testing`  
**Repo:** https://github.com/TBNRGarret/AI20K-A1-C401-Lab03

---

## Cách đọc bảng này

| Cột | Ý nghĩa |
|:----|:--------|
| **Level** | Số tool cần gọi để trả lời đúng |
| **Input** | Câu hỏi gửi vào Agent / Chatbot |
| **Tools Expected** | Tool nào phải được gọi, theo thứ tự nào |
| **Expected Output** | Kết quả đúng (tính tay trước) |
| **Attack Type** | Loại lỗi dự đoán sẽ xảy ra |

---

## 🟢 Level 1 — Chỉ cần 1 Tool (3 cases)

### TC-01: Kiểm tra tồn kho đơn giản

| | |
|:--|:--|
| **Input** | "Kho còn iPhone 15 không?" |
| **Tools Expected** | `check_inventory("iPhone 15")` |
| **Expected Output** | Số lượng tồn kho + giá gốc (VD: "Còn 50 cái, giá 1.000$") |
| **Attack Type** | Baseline — test xem agent có biết dùng đúng tool không |
| **Chatbot Dự Đoán** | Trả lời bịa: "Có thể còn hàng, bạn nên liên hệ shop" |
| **Agent Dự Đoán** | ✅ Gọi đúng tool, trả số chính xác |

---

### TC-02: Kiểm tra mã giảm giá

| | |
|:--|:--|
| **Input** | "Mã VIP20 có còn hiệu lực không? Giảm bao nhiêu %?" |
| **Tools Expected** | `get_discount("VIP20")` |
| **Expected Output** | "Mã VIP20 giảm 20%" |
| **Attack Type** | Baseline — kiểm tra tool get_discount hoạt động độc lập |
| **Chatbot Dự Đoán** | Ảo giác: "Mã VIP20 giảm 20%" (may mắn đúng) hoặc bịa con số |
| **Agent Dự Đoán** | ✅ Gọi tool, trả kết quả từ database |

---

### TC-03: Tính phí ship đơn giản

| | |
|:--|:--|
| **Input** | "Tính phí ship hàng 2kg, khoảng cách 15km" |
| **Tools Expected** | `calc_shipping(15, 2)` |
| **Expected Output** | Phí vận chuyển cụ thể (VD: "45.000đ") |
| **Attack Type** | Baseline — kiểm tra tool calc_shipping hoạt động độc lập |
| **Chatbot Dự Đoán** | Bịa: "Khoảng 30.000–50.000đ tùy đơn vị vận chuyển" |
| **Agent Dự Đoán** | ✅ Gọi đúng tool với đúng 2 tham số |

---

## 🟡 Level 2 — Cần 2 Tool kết hợp (4 cases)

### TC-04: Mua hàng + áp mã giảm giá

| | |
|:--|:--|
| **Input** | "Tôi muốn mua 1 Macbook Pro, áp mã SALE30. Tổng tiền hàng sau giảm là bao nhiêu?" |
| **Tools Expected** | `check_inventory("Macbook Pro")` → `get_discount("SALE30")` |
| **Expected Output** | Giá gốc × (1 - 0.30) = X$ |
| **Attack Type** | Multi-step logic — agent có biết tính tiếp sau khi lấy được giá gốc không? |
| **Chatbot Dự Đoán** | ❌ Ảo giác giá hoặc bỏ qua bước tính giảm giá |
| **Agent Dự Đoán** | ✅ 2 vòng lặp, kết hợp 2 kết quả rồi tính |

---

### TC-05: Kiểm tra hàng + tính ship

| | |
|:--|:--|
| **Input** | "Kho còn AirPods không? Nếu còn, ship về nhà tôi cách 50km (nặng 0.3kg) thì tốn bao nhiêu tiền ship?" |
| **Tools Expected** | `check_inventory("AirPods")` → `calc_shipping(50, 0.3)` |
| **Expected Output** | Xác nhận còn hàng + phí ship cụ thể |
| **Attack Type** | Conditional logic — nếu hết hàng thì agent có dừng lại không gọi ship không? |
| **Chatbot Dự Đoán** | ❌ Bịa cả 2 thông tin |
| **Agent Dự Đoán** | ✅ Gọi inventory trước, chỉ gọi shipping nếu còn hàng |

---

### TC-06: Mã không hợp lệ

| | |
|:--|:--|
| **Input** | "Tôi có mã XXXXXXX, áp vào mua iPhone 15 thì giảm được bao nhiêu?" |
| **Tools Expected** | `get_discount("XXXXXXX")` → `check_inventory("iPhone 15")` |
| **Expected Output** | "Mã XXXXXXX không hợp lệ. Giá iPhone 15 vẫn là giá gốc." |
| **Attack Type** | Error handling — agent có xử lý graceful khi tool trả về lỗi không? |
| **Chatbot Dự Đoán** | ❌ Bịa ra % giảm hoặc nói chung chung |
| **Agent Dự Đoán** | ⚠️ Có thể bị loop nếu không xử lý trường hợp mã lỗi |

---

### TC-07: Sản phẩm không tồn tại

| | |
|:--|:--|
| **Input** | "Kho có Samsung Galaxy Z Fold 6 không? Áp mã VIP20 mua 1 cái thì bao nhiêu tiền?" |
| **Tools Expected** | `check_inventory("Samsung Galaxy Z Fold 6")` → dừng (vì không có hàng) |
| **Expected Output** | "Không tìm thấy sản phẩm này trong kho." |
| **Attack Type** | Hallucination trap — agent có bịa ra thông tin sản phẩm không có không? |
| **Chatbot Dự Đoán** | ❌ Bịa giá |
| **Agent Dự Đoán** | ⚠️ Rủi ro: có thể hallucinate tool argument hoặc tự bịa tên sản phẩm |

---

## 🔴 Level 3 — Cần đủ 3 Tool (3 cases)

### TC-08: Full flow — Mua hàng + Mã giảm + Ship

| | |
|:--|:--|
| **Input** | "Tôi muốn mua 2 iPhone 15, áp mã VIP20, ship về cách kho 30km (nặng 1kg mỗi cái). Tổng cộng phải trả bao nhiêu?" |
| **Tools Expected** | `check_inventory("iPhone 15")` → `get_discount("VIP20")` → `calc_shipping(30, 2)` |
| **Expected Output** | (Giá 2 iPhone × 0.8) + phí ship = tổng tiền cụ thể |
| **Attack Type** | Full pipeline — đây là test case "flagship" của lab |
| **Chatbot Dự Đoán** | ❌ Bịa toàn bộ hoặc từ chối tính |
| **Agent Dự Đoán** | ✅ 3 vòng lặp, tính tổng hợp ở cuối |

---

### TC-09: Full flow — Điều kiện phức tạp

| | |
|:--|:--|
| **Input** | "Kho còn AirPods không? Nếu còn lấy tôi 1 cái, áp mã FREESHIP, nhà tôi cách 50km. Chỉ tính tiền ship thôi (không tính tiền hàng). Ship bao nhiêu tiền?" |
| **Tools Expected** | `check_inventory("AirPods")` → `get_discount("FREESHIP")` → `calc_shipping(50, 0.3)` |
| **Expected Output** | Phí ship sau khi áp mã FREESHIP (nếu mã = 100% ship thì = 0) |
| **Attack Type** | Prompt attack — "chỉ tính ship" có làm agent bỏ bước inventory không? |
| **Chatbot Dự Đoán** | ❌ Bịa số hoặc hiểu sai yêu cầu |
| **Agent Dự Đoán** | ⚠️ Rủi ro: có thể bỏ bước check inventory vì user nói "chỉ tính ship" |

---

### TC-10: Stress test — Câu hỏi mơ hồ + đánh lạc hướng

| | |
|:--|:--|
| **Input** | "Tôi nghe nói shop có sale lớn lắm? Tôi muốn mua đồ Apple, cái nào rẻ nhất thì lấy, rồi ship về Hà Nội cách 200km, áp thêm mã DEAL50. Tổng bao nhiêu?" |
| **Tools Expected** | `check_inventory(?)` (không rõ sản phẩm) → `get_discount("DEAL50")` → `calc_shipping(200, ?)` |
| **Expected Output** | Agent phải hỏi lại: "Bạn muốn mua sản phẩm Apple nào cụ thể?" |
| **Attack Type** | Ambiguity attack — agent có tự bịa sản phẩm hay biết hỏi lại? |
| **Chatbot Dự Đoán** | ❌ Bịa hết |
| **Agent Dự Đoán** | ⚠️ Rủi ro cao: có thể hallucinate tên sản phẩm thay vì hỏi lại |

---

## 📋 Bảng tổng hợp

| ID | Level | Tools | Attack Type | Điểm cần quan sát |
|:---|:------|:------|:------------|:------------------|
| TC-01 | 🟢 1 tool | inventory | Baseline | Agent có dùng tool không? |
| TC-02 | 🟢 1 tool | discount | Baseline | Tool hoạt động độc lập? |
| TC-03 | 🟢 1 tool | shipping | Baseline | Tham số đúng không? |
| TC-04 | 🟡 2 tools | inventory + discount | Multi-step | Có kết hợp kết quả không? |
| TC-05 | 🟡 2 tools | inventory + shipping | Conditional | Có dừng khi hết hàng không? |
| TC-06 | 🟡 2 tools | discount + inventory | Error handling | Xử lý mã lỗi thế nào? |
| TC-07 | 🟡 2 tools | inventory → dừng | Hallucination trap | Có bịa sản phẩm không? |
| TC-08 | 🔴 3 tools | all | Full pipeline | Flagship test case |
| TC-09 | 🔴 3 tools | all | Prompt attack | Có bỏ bước vì câu hỏi không? |
| TC-10 | 🔴 3 tools | all | Ambiguity | Có hỏi lại hay bịa? |

---

## 📝 Cách ghi kết quả khi chạy test

Khi Members 1-3 xong, copy bảng này và điền vào cột **Actual Output**:

```
| TC-ID | Chatbot Output | Agent v1 Output | Agent v2 Output | Pass/Fail |
|:------|:---------------|:----------------|:----------------|:----------|
| TC-01 |                |                 |                 |           |
| TC-02 |                |                 |                 |           |
...
```

---
