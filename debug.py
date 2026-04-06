import os
from dotenv import load_dotenv

# Nạp file .env
load_dotenv()

key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("DEFAULT_MODEL")

print("--- KIỂM TRA BIẾN MÔI TRƯỜNG ---")
if key:
    print(f"✅ Đã thấy Key: {key[:10]}... (Tổng {len(key)} ký tự)")
else:
    print("❌ KHÔNG THẤY OPENROUTER_API_KEY! Kiểm tra lại tên file .env")

if model:
    print(f"✅ Model hiện tại: {model}")
else:
    print("❌ Không thấy DEFAULT_MODEL")