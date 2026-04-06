import os
import sys
import json
from dotenv import load_dotenv

# Thêm đường dẫn vào hệ thống
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActAgent
import src.tools.tools as all_tools

def tool_executor(action: str, action_input: str) -> str:
    """
    Hàm cầu nối để gọi các tool thực tế dựa trên yêu cầu từ Agent của Hoang.
    """
    func = getattr(all_tools, action, None)
    if not func:
        return f'{{"error": "Không tìm thấy công cụ {action}"}}'
    
    try:
        # Xử lý tham số: tách dấu phẩy và chuyển đổi kiểu dữ liệu (số/chuỗi)
        args = [a.strip() for a in action_input.split(",")] if action_input else []
        processed_args = []
        for arg in args:
            if not arg: continue
            try:
                if "." in arg: processed_args.append(float(arg))
                else: processed_args.append(int(arg))
            except:
                processed_args.append(arg)
        
        # Gọi hàm tool thực tế trong src/tools/tools.py
        result = func(*processed_args)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f'{{"error": "Lỗi thực thi: {str(e)}"}}'

def test_v1_agent():
    load_dotenv()
    
    # Dùng Gemini Provider trực tiếp (Yêu cầu phải có GEMINI_API_KEY thực trong .env)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or "your_gemini_api_key_here" in api_key:
        print("❌ LỖI: Bạn chưa điền GEMINI_API_KEY thực tế vào file .env.")
        print("Hãy truy cập https://aistudio.google.com/ để lấy key miễn phí.")
        return

    # Khởi tạo Gemini Provider
    provider = GeminiProvider(model_name=model_name, api_key=api_key)
    
    # Khởi tạo Agent v1 theo đúng format của Hoang
    agent = ReActAgent(
        llm=provider,
        tool_executor=tool_executor,
        max_steps=8
    )
    
    prompt = "Tôi muốn mua iphone 15, khoảng cách ship là 5km, nặng 0.5kg. Tôi có mã giảm giá GIAM20. Hãy tính tổng chi phí thanh toán cho tôi."
    
    print(f"--- [TEST AGENT V1] ---")
    print(f"Model: {model_name}")
    print(f"User: {prompt}\n")
    
    try:
        final_answer = agent.run(prompt)
        print(f"\n✅ KẾT QUẢ CUỐI CÙNG:\n{final_answer}")
    except Exception as e:
        print(f"\n❌ LỖI KHI CHẠY TEST: {e}")

if __name__ == "__main__":
    test_v1_agent()
