import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load biến môi trường từ file .env
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model = "qwen/qwen3.6-plus:free"

print(f"--- Đang kiểm tra kết nối tới OpenRouter ---")
print(f"Model: {model}")

if not api_key:
    print("❌ Lỗi: Không tìm thấy OPENROUTER_API_KEY trong file .env!")
    exit()

# 2. Khởi tạo client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

try:
    start_time = time.time()
    
    # 3. Gửi một request siêu ngắn
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Say 'OK' if you can hear me."}],
        # Thử nghiệm tính năng reasoning luôn
        extra_body={"reasoning": {"enabled": True}}
    )

    latency = int((time.time() - start_time) * 1000)
    
    # 4. In kết quả
    print(f"✅ Kết nối thành công! ({latency}ms)")
    print(f"AI phản hồi: {response.choices[0].message.content}")
    
    # Kiểm tra xem có reasoning không
    if hasattr(response.choices[0].message, 'reasoning_details'):
        print("🧠 Đã nhận được dữ liệu Reasoning (Tư duy logic).")
    else:
        print("ℹ️ Model phản hồi nhưng không kèm theo Reasoning.")

except Exception as e:
    print(f"❌ Lỗi kết nối API: {e}")