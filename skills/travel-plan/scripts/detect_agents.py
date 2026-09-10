#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""偵測當前系統可呼叫哪些外部 agent CLI，並依專長給出派工建議。

用途：`SKILL.md` 啟動順序第 1 步「能力自檢」的子agent項目。
主 agent 自己的 Task/Agent 工具無法從 shell 偵測，需由主 agent 自行填入
（見 --self 參數）；本腳本只負責偵測 **外部 CLI executor**。

三條鐵則（見 references/portability.md）：
  1. 這支 script 不是必要路徑——無 Python 時走 references/checklists/detect_agents.md。
  2. 偵測失敗不得中斷流程：任何探測異常一律降級為「不可用」，本腳本永遠 exit 0。
  3. 只做偵測與分類，不做派工決定——派工由主 agent 依 references/agent_routing.md 判斷。

用法：
    python3 detect_agents.py                # 人類可讀表格
    python3 detect_agents.py --json         # 機器可讀
    python3 detect_agents.py --no-smoke     # 只看 binary 在不在，不實際呼叫（不耗 token）
    python3 detect_agents.py --self sonnet  # 併入主 agent 自己的子agent能力
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

# ---------------------------------------------------------------------------
# Executor 登錄表
#
# smoke.expect_substr: 冒煙測試「成功」的判準。不能只看 exit code——
# 實測遇過 binary 存在但只是個未安裝的 stub，會跳互動式安裝提示，
# 此時 exit code 仍可能為 0。見 fail_substr。
# ---------------------------------------------------------------------------
REGISTRY = [
    {
        "name": "agy",
        "label": "Google Antigravity CLI",
        "bin": "agy",
        "family": "gemini",
        "models_cmd": ["agy", "models"],
        "models_grep": "flash",
        "smoke": {
            "cmd": ["agy", "-p", "回覆兩個字：可用", "--print-timeout", "2m"],
            "expect_substr": "可用",
        },
        "invoke_hint": 'agy -p "<task>" --model <model> --print-timeout 15m',
    },
    {
        "name": "copilot",
        "label": "GitHub Copilot CLI",
        "bin": "copilot",
        "family": "claude",
        "models_cmd": None,
        "models_grep": None,
        "smoke": {
            "cmd": ["copilot", "-p", "回覆兩個字：可用", "--allow-all-tools"],
            "expect_substr": "可用",
        },
        "invoke_hint": 'copilot -p "<task>" --allow-all-tools --add-dir <logdir> --model <model>',
    },
    {
        "name": "gemini",
        "label": "Google Gemini CLI",
        "bin": "gemini",
        "family": "gemini",
        "models_cmd": None,
        "models_grep": None,
        "smoke": {
            "cmd": ["gemini", "-p", "回覆兩個字：可用"],
            "expect_substr": "可用",
        },
        "invoke_hint": 'gemini -p "<task>"',
    },
    {
        "name": "codex",
        "label": "OpenAI Codex CLI",
        "bin": "codex",
        "family": "openai",
        "models_cmd": None,
        "models_grep": None,
        "smoke": {
            "cmd": ["codex", "exec", "回覆兩個字：可用"],
            "expect_substr": "可用",
        },
        "invoke_hint": 'codex exec "<task>"',
    },
]

# binary 存在但其實沒裝好／未登入時的典型輸出。命中即判定不可用。
FAIL_SUBSTR = (
    "cannot find",
    "not installed",
    "install ",
    "please run",
    "not logged in",
    "unauthorized",
    "authentication",
    "command not found",
    "eligibility check failed",
)

SMOKE_TIMEOUT = 150  # 秒


def run(cmd, timeout):
    """執行外部指令，永不拋例外。回傳 (exit_code, output)。"""
    try:
        p = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,  # 關鍵：避免 stub 卡在互動式安裝提示
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True,
            errors="replace",
        )
        return p.returncode, (p.stdout or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "<timeout>"
    except Exception as e:  # noqa: BLE001 - 鐵則 2：任何異常都降級，不中斷
        return 125, f"<error: {e.__class__.__name__}: {e}>"


def probe(entry, do_smoke):
    """探測單一 executor。回傳結果 dict。"""
    res = {
        "name": entry["name"],
        "label": entry["label"],
        "family": entry["family"],
        "path": None,
        "status": "absent",       # absent | present_untested | broken | ready
        "detail": "",
        "models": [],
        "invoke_hint": entry["invoke_hint"],
    }

    path = shutil.which(entry["bin"])
    if not path:
        res["detail"] = "binary 不在 PATH"
        return res
    res["path"] = path

    if not do_smoke:
        res["status"] = "present_untested"
        res["detail"] = "binary 存在，未實際呼叫驗證（--no-smoke）"
        return res

    code, out = run(entry["smoke"]["cmd"], SMOKE_TIMEOUT)
    low = out.lower()

    if any(s in low for s in FAIL_SUBSTR):
        res["status"] = "broken"
        # 只留第一行，避免把整段安裝說明灌進 context
        res["detail"] = "binary 存在但無法使用：" + out.splitlines()[0][:120]
        return res

    if code != 0:
        res["status"] = "broken"
        res["detail"] = f"冒煙測試 exit={code}：{out.splitlines()[0][:120] if out else '(無輸出)'}"
        return res

    if entry["smoke"]["expect_substr"] not in out:
        res["status"] = "broken"
        res["detail"] = f"冒煙測試回應不符預期：{out[:120]!r}"
        return res

    res["status"] = "ready"
    res["detail"] = "冒煙測試通過"

    if entry.get("models_cmd"):
        mcode, mout = run(entry["models_cmd"], 30)
        if mcode == 0 and mout:
            models = [
                ln.split()[0]
                for ln in mout.splitlines()
                if ln.strip()
                and (not entry["models_grep"] or entry["models_grep"] in ln.lower())
            ]
            res["models"] = models[:10]
    return res


def main():
    ap = argparse.ArgumentParser(description="偵測可呼叫的外部 agent CLI 並給派工建議")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    ap.add_argument("--no-smoke", action="store_true",
                    help="只檢查 binary 是否存在，不實際呼叫（不耗 token，但無法排除未安裝的 stub）")
    ap.add_argument("--self", metavar="MODEL", default=None,
                    help="主 agent 自己的子agent能力所用模型（如 sonnet）。由主 agent 自行填入。")
    args = ap.parse_args()

    results = [probe(e, not args.no_smoke) for e in REGISTRY]

    if args.self:
        results.insert(0, {
            "name": "self-subagent",
            "label": "主 agent 內建子agent（Task/Agent 工具）",
            "family": "claude",
            "path": "<in-process>",
            "status": "ready",
            "detail": "由主 agent 宣告，非本腳本偵測",
            "models": [args.self],
            "invoke_hint": "主 agent 的 Task/Agent 工具",
        })

    ready = [r for r in results if r["status"] == "ready"]
    payload = {
        "ready_count": len(ready),
        "mode_hint": "序列" if not ready else "混合",
        "executors": results,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("=== 可呼叫 agent 偵測 ===")
    if args.no_smoke:
        print("（--no-smoke：僅檢查 binary，未實際呼叫；present_untested 不可直接當成可用）\n")
    icon = {"ready": "✓", "broken": "✗", "absent": "－", "present_untested": "?"}
    for r in results:
        print(f"{icon[r['status']]} {r['name']:<14} [{r['status']}] {r['label']}")
        print(f"    {r['detail']}")
        if r["models"]:
            print(f"    可用模型：{', '.join(r['models'])}")
        if r["status"] == "ready":
            print(f"    呼叫方式：{r['invoke_hint']}")
    print()
    print(f"可用 executor：{len(ready)} 個 → 建議模式：{payload['mode_hint']}")
    if ready:
        print("派工分工請讀 references/agent_routing.md（依專長分派，不是隨便挑一個）。")
    else:
        print("無任何外部 executor 可用。若主 agent 本身也無子agent能力，走序列模式。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
