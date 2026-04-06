"""
run_tests.py — QA Test Runner
Member 4: QA & Prompt Attacker
Branch: feature/qa-testing

Cách dùng:
    python tests/run_tests.py --mode agent    # chạy Agent
    python tests/run_tests.py --mode chatbot  # chạy Chatbot
    python tests/run_tests.py --mode both     # chạy cả hai, so sánh kết quả
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

# ───────────────────────────────────────────────
# 10 TEST CASES (sync với test_cases.md)
# ───────────────────────────────────────────────

TEST_CASES = [
    {
        "id": "TC-01",
        "level": 1,
        "description": "Kiểm tra tồn kho đơn giản",
        "input": "Kho còn iPhone 15 không?",
        "tools_expected": ["check_inventory"],
        "attack_type": "Baseline",
        "note": "Agent phải gọi check_inventory, không được bịa số"
    },
    {
        "id": "TC-02",
        "level": 1,
        "description": "Kiểm tra mã giảm giá",
        "input": "Mã VIP20 có còn hiệu lực không? Giảm bao nhiêu %?",
        "tools_expected": ["get_discount"],
        "attack_type": "Baseline",
        "note": "Agent phải gọi get_discount, không tự bịa %"
    },
    {
        "id": "TC-03",
        "level": 1,
        "description": "Tính phí ship đơn giản",
        "input": "Tính phí ship hàng 2kg, khoảng cách 15km",
        "tools_expected": ["calc_shipping"],
        "attack_type": "Baseline",
        "note": "Phải truyền đúng 2 tham số: distance=15, weight=2"
    },
    {
        "id": "TC-04",
        "level": 2,
        "description": "Mua hàng + áp mã giảm giá",
        "input": "Tôi muốn mua 1 Macbook Pro, áp mã SALE30. Tổng tiền hàng sau giảm là bao nhiêu?",
        "tools_expected": ["check_inventory", "get_discount"],
        "attack_type": "Multi-step",
        "note": "Phải kết hợp kết quả 2 tool để tính giá cuối"
    },
    {
        "id": "TC-05",
        "level": 2,
        "description": "Kiểm tra hàng + tính ship",
        "input": "Kho còn AirPods không? Nếu còn, ship về nhà tôi cách 50km (nặng 0.3kg) thì tốn bao nhiêu tiền ship?",
        "tools_expected": ["check_inventory", "calc_shipping"],
        "attack_type": "Conditional",
        "note": "Nếu hết hàng → dừng, không gọi calc_shipping"
    },
    {
        "id": "TC-06",
        "level": 2,
        "description": "Mã không hợp lệ",
        "input": "Tôi có mã XXXXXXX, áp vào mua iPhone 15 thì giảm được bao nhiêu?",
        "tools_expected": ["get_discount", "check_inventory"],
        "attack_type": "Error handling",
        "note": "Khi tool trả về lỗi, agent phải xử lý graceful, không loop"
    },
    {
        "id": "TC-07",
        "level": 2,
        "description": "Sản phẩm không tồn tại",
        "input": "Kho có Samsung Galaxy Z Fold 6 không? Áp mã VIP20 mua 1 cái thì bao nhiêu tiền?",
        "tools_expected": ["check_inventory"],
        "attack_type": "Hallucination trap",
        "note": "Agent KHÔNG được bịa giá sản phẩm không có trong DB"
    },
    {
        "id": "TC-08",
        "level": 3,
        "description": "Full flow — Flagship test case",
        "input": "Tôi muốn mua 2 iPhone 15, áp mã VIP20, ship về cách kho 30km (nặng 1kg mỗi cái). Tổng cộng phải trả bao nhiêu?",
        "tools_expected": ["check_inventory", "get_discount", "calc_shipping"],
        "attack_type": "Full pipeline",
        "note": "Test case quan trọng nhất. Phải gọi đủ 3 tool theo đúng thứ tự"
    },
    {
        "id": "TC-09",
        "level": 3,
        "description": "Full flow — Điều kiện phức tạp",
        "input": "Kho còn AirPods không? Nếu còn lấy tôi 1 cái, áp mã FREESHIP, nhà tôi cách 50km. Chỉ tính tiền ship thôi (không tính tiền hàng). Ship bao nhiêu tiền?",
        "tools_expected": ["check_inventory", "get_discount", "calc_shipping"],
        "attack_type": "Prompt attack",
        "note": "'Chỉ tính ship' không có nghĩa là bỏ bước check inventory"
    },
    {
        "id": "TC-10",
        "level": 3,
        "description": "Stress test — Câu hỏi mơ hồ",
        "input": "Tôi nghe nói shop có sale lớn lắm? Tôi muốn mua đồ Apple, cái nào rẻ nhất thì lấy, rồi ship về Hà Nội cách 200km, áp thêm mã DEAL50. Tổng bao nhiêu?",
        "tools_expected": ["check_inventory", "get_discount", "calc_shipping"],
        "attack_type": "Ambiguity",
        "note": "Không có tên sản phẩm cụ thể → agent phải hỏi lại, không được tự bịa"
    },
]


# ───────────────────────────────────────────────
# RESULT LOGGER
# ───────────────────────────────────────────────

class TestResultLogger:
    def __init__(self):
        self.results = []
        os.makedirs("tests/results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = f"tests/results/run_{timestamp}.json"
        self.markdown_file = f"tests/results/run_{timestamp}.md"

    def record(self, tc_id: str, mode: str, output: str, latency_ms: int,
               tools_called: list, steps: int, error: str = None):
        result = {
            "tc_id": tc_id,
            "mode": mode,
            "output": output,
            "latency_ms": latency_ms,
            "tools_called": tools_called,
            "steps": steps,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.results.append(result)
        return result

    def save_json(self):
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n📁 JSON saved → {self.output_file}")

    def save_markdown(self, chatbot_results: dict, agent_results: dict):
        lines = [
            "# Test Run Report",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "| TC | Level | Attack Type | Chatbot | Agent | Winner |",
            "|:---|:------|:------------|:--------|:------|:-------|",
        ]
        for tc in TEST_CASES:
            tc_id = tc["id"]
            cb = chatbot_results.get(tc_id, {})
            ag = agent_results.get(tc_id, {})

            cb_status = "❌ Error" if cb.get("error") else f"✅ {cb.get('latency_ms', '?')}ms"
            ag_status = "❌ Error" if ag.get("error") else f"✅ {ag.get('latency_ms', '?')}ms"

            # Simple winner logic: agent wins if it called the right tools
            winner = "Agent" if ag.get("tools_called") else "Draw"

            lines.append(
                f"| {tc_id} | L{tc['level']} | {tc['attack_type']} "
                f"| {cb_status} | {ag_status} | {winner} |"
            )

        lines += [
            "",
            "## Raw Outputs",
            ""
        ]
        for tc in TEST_CASES:
            tc_id = tc["id"]
            cb = chatbot_results.get(tc_id, {})
            ag = agent_results.get(tc_id, {})
            lines += [
                f"### {tc_id} — {tc['description']}",
                f"**Input**: `{tc['input']}`",
                "",
                f"**Chatbot**: {cb.get('output', 'N/A')}",
                "",
                f"**Agent**: {ag.get('output', 'N/A')}",
                f"**Tools called**: {ag.get('tools_called', [])}",
                f"**Steps**: {ag.get('steps', '?')}",
                "",
                "---",
                ""
            ]

        with open(self.markdown_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"📄 Markdown saved → {self.markdown_file}")


# ───────────────────────────────────────────────
# MOCK RUNNER (dùng khi chưa có Agent/Chatbot thật)
# Thay thế bằng import thật khi Members 1-3 xong
# ───────────────────────────────────────────────

def run_mock_chatbot(user_input: str) -> dict:
    """
    Placeholder — thay bằng import Chatbot thật khi có code.
    Giả lập chatbot: trả lời bịa, không gọi tool nào.
    """
    time.sleep(0.3)  # Giả lập latency
    return {
        "output": f"[MOCK CHATBOT] Đây là câu trả lời giả cho: '{user_input[:40]}...'",
        "latency_ms": 300,
        "tools_called": [],
        "steps": 0,
        "error": None
    }


def run_mock_agent(user_input: str) -> dict:
    """
    Placeholder — thay bằng import Agent thật khi có code.
    Giả lập agent: có gọi tool.
    """
    time.sleep(0.5)
    return {
        "output": f"[MOCK AGENT] Đây là câu trả lời có tool cho: '{user_input[:40]}...'",
        "latency_ms": 500,
        "tools_called": ["check_inventory"],  # giả lập
        "steps": 2,
        "error": None
    }


def run_real_chatbot(user_input: str) -> dict:
    """
    TODO (Member 3 xong thì uncomment):
    from src.chatbot import Chatbot
    from src.core.openai_provider import OpenAIProvider
    llm = OpenAIProvider()
    bot = Chatbot(llm)
    ...
    """
    raise NotImplementedError("Uncomment khi Member 3 push code chatbot.py")


def run_real_agent(user_input: str) -> dict:
    """
    TODO (Member 1 + 2 xong thì uncomment):
    from src.agent.agent import ReActAgent
    from src.core.openai_provider import OpenAIProvider
    from src.tools.inventory import check_inventory
    from src.tools.discount import get_discount
    from src.tools.shipping import calc_shipping
    ...
    """
    raise NotImplementedError("Uncomment khi Member 1 & 2 push code agent.py + tools")


# ───────────────────────────────────────────────
# MAIN RUNNER
# ───────────────────────────────────────────────

def run_suite(mode: str, use_mock: bool = True):
    log = TestResultLogger()
    chatbot_results = {}
    agent_results = {}

    print(f"\n{'='*60}")
    print(f"  🚀 QA TEST SUITE — Mode: {mode.upper()}")
    print(f"  {'Mock' if use_mock else 'Real'} mode | {len(TEST_CASES)} test cases")
    print(f"{'='*60}\n")

    for tc in TEST_CASES:
        tc_id = tc["id"]
        user_input = tc["input"]
        print(f"[{tc_id}] L{tc['level']} | {tc['attack_type']}")
        print(f"  Input: {user_input[:70]}...")

        # ── CHATBOT ──
        if mode in ("chatbot", "both"):
            try:
                if use_mock:
                    res = run_mock_chatbot(user_input)
                else:
                    res = run_real_chatbot(user_input)
                chatbot_results[tc_id] = res
                print(f"  🤖 Chatbot ({res['latency_ms']}ms): {res['output'][:80]}")
            except Exception as e:
                chatbot_results[tc_id] = {"output": str(e), "error": str(e),
                                          "latency_ms": 0, "tools_called": [], "steps": 0}
                print(f"  🤖 Chatbot ❌ {e}")

        # ── AGENT ──
        if mode in ("agent", "both"):
            try:
                if use_mock:
                    res = run_mock_agent(user_input)
                else:
                    res = run_real_agent(user_input)
                agent_results[tc_id] = res
                print(f"  🧠 Agent  ({res['latency_ms']}ms | {res['steps']} steps "
                      f"| tools: {res['tools_called']})")
                print(f"           {res['output'][:80]}")
            except Exception as e:
                agent_results[tc_id] = {"output": str(e), "error": str(e),
                                        "latency_ms": 0, "tools_called": [], "steps": 0}
                print(f"  🧠 Agent  ❌ {e}")

        print()

    # ── SAVE RESULTS ──
    log.results = list(chatbot_results.values()) + list(agent_results.values())
    log.save_json()
    if mode == "both":
        log.save_markdown(chatbot_results, agent_results)

    # ── SUMMARY ──
    print(f"\n{'='*60}")
    print("  📊 SUMMARY")
    print(f"{'='*60}")
    if mode in ("agent", "both"):
        errors = sum(1 for r in agent_results.values() if r.get("error"))
        avg_latency = sum(r["latency_ms"] for r in agent_results.values()) / len(agent_results)
        avg_steps = sum(r["steps"] for r in agent_results.values()) / len(agent_results)
        print(f"  Agent   | Errors: {errors}/{len(TEST_CASES)} | "
              f"Avg latency: {avg_latency:.0f}ms | Avg steps: {avg_steps:.1f}")
    if mode in ("chatbot", "both"):
        errors = sum(1 for r in chatbot_results.values() if r.get("error"))
        avg_latency = sum(r["latency_ms"] for r in chatbot_results.values()) / len(chatbot_results)
        print(f"  Chatbot | Errors: {errors}/{len(TEST_CASES)} | "
              f"Avg latency: {avg_latency:.0f}ms")
    print()


# ───────────────────────────────────────────────
# ENTRY POINT
# ───────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA Test Runner — Smart E-commerce Agent")
    parser.add_argument("--mode", choices=["agent", "chatbot", "both"],
                        default="both", help="Chạy agent, chatbot, hoặc cả hai")
    parser.add_argument("--real", action="store_true",
                        help="Dùng code thật (mặc định: mock)")
    args = parser.parse_args()

    run_suite(mode=args.mode, use_mock=not args.real)