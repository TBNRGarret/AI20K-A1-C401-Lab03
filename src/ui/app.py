import os
import sys
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Thêm đường dẫn dự án vào hệ thống
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActAgent
import src.tools.tools as all_tools

load_dotenv()

app = FastAPI(title="Smart Agent UI Backend")

# --- Logic Agent ---

def web_tool_executor(action: str, action_input: str) -> str:
    """Gọi tool thực tế và trả về kết quả cho Agent."""
    func = getattr(all_tools, action, None)
    if not func:
        return f'{{"error": "Không tìm thấy công cụ {action}"}}'
    
    try:
        args = [a.strip() for a in action_input.split(",")] if action_input else []
        processed_args = []
        for arg in args:
            if not arg: continue
            try:
                if "." in arg: processed_args.append(float(arg))
                else: processed_args.append(int(arg))
            except:
                processed_args.append(arg)
        
        result = func(*processed_args)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f'{{"error": "Lỗi: {str(e)}"}}'

# --- Khởi tạo Agent Toàn Cục (Trí nhớ dài hạn) ---
AGENT_INSTANCE: Optional[ReActAgent] = None

def get_agent():
    global AGENT_INSTANCE
    if AGENT_INSTANCE is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or "your_gemini_api_key_here" in api_key:
            return None
        
        provider = GeminiProvider(model_name="gemini-2.5-flash", api_key=api_key)
        AGENT_INSTANCE = ReActAgent(llm=provider, tool_executor=web_tool_executor)
    return AGENT_INSTANCE

# --- API Endpoints ---

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    agent = get_agent()
    if not agent:
        raise HTTPException(status_code=400, detail="Thiếu GEMINI_API_KEY hoặc lỗi khởi tạo Agent.")

    # Chạy agent logic (giữ nguyên history)
    try:
        final_answer = agent.run(req.message)
        print(f"DEBUG: Agent Response -> {final_answer}")
        
        return {
            "answer": final_answer,
            "status": "success"
        }
    except Exception as e:
        print(f"DEBUG: Agent Error -> {str(e)}")
        return {"error": str(e), "status": "failed"}

@app.post("/reset")
async def reset_chat():
    global AGENT_INSTANCE
    AGENT_INSTANCE = None # Reset instance để tạo mới Agent (trống history)
    print("DEBUG: Lịch sử Chat đã được xóa sạch.")
    return {"message": "Chat history reset successfully", "status": "success"}

# Phục vụ file Static (UI)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    print("\n🚀 Smart Agent Web UI đang khởi động tại http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
