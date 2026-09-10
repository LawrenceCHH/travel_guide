# 手動核對：可呼叫 agent 偵測（`detect_agents.py` 的 md 後備）

> 無 Python 或 script 執行失敗時使用。目標是得出與 `scripts/detect_agents.py` 相同的判定。
> 判定後的派工分工見 `references/agent_routing.md`。

依序執行，**每個 executor 都要走完步驟 1→3 才能判定**。

---

## 步驟 1：binary 在不在

對下列每個名稱執行 `command -v <name>`：

| name | 說明 |
|---|---|
| `agy` | Google Antigravity CLI |
| `copilot` | GitHub Copilot CLI |
| `gemini` | Google Gemini CLI |
| `codex` | OpenAI Codex CLI |

- 無輸出 → 判定 `absent`，這個 executor 到此為止，不必做步驟 2。
- 有輸出（印出路徑）→ 記下路徑，繼續步驟 2。

## 步驟 2：冒煙測試（**不可省略**）

**binary 存在不等於可用。** 必須實際呼叫一次。對步驟 1 有輸出的每個 executor：

| name | 冒煙指令 |
|---|---|
| `agy` | `agy -p "回覆兩個字：可用" --print-timeout 2m < /dev/null` |
| `copilot` | `copilot -p "回覆兩個字：可用" --allow-all-tools < /dev/null` |
| `gemini` | `gemini -p "回覆兩個字：可用" < /dev/null` |
| `codex` | `codex exec "回覆兩個字：可用" < /dev/null` |

**指令結尾的 `< /dev/null` 不可省略**——未安裝的 stub 會跳互動式安裝提示，
沒有這一段會卡住等輸入。

## 步驟 3：判讀輸出

依序檢查，命中即停：

1. 輸出（不分大小寫）含下列任一字串 → 判定 `broken`：
   `cannot find`、`not installed`、`install `、`please run`、`not logged in`、
   `unauthorized`、`authentication`、`command not found`、`eligibility check failed`
2. exit code 非 0 → 判定 `broken`。
3. 輸出不含「可用」兩字 → 判定 `broken`。
4. 以上皆非 → 判定 `ready`。

> 步驟 3 的順序不可調換：實測遇過 `copilot` 的 stub 印出安裝提示、exit code 仍為 0
> 的情況，只看 exit code 會誤判為可用。

## 步驟 4：補查可用模型（僅 `ready` 者）

- `agy`：`agy models | grep flash` → 取編號最高的 `*-flash-high`。
- 其餘：若該 CLI 無 models 子指令，留空，派工時用其預設模型。

## 步驟 5：加入主 agent 自己的子agent能力

本 checklist 只涵蓋外部 CLI。主 agent 若本身具備 Task/Agent 工具，
自行加一列 `self-subagent` = `ready`，並記下所用模型。

## 步驟 6：結論

- `ready` 數量（含 `self-subagent`）為 0 → **序列模式**。
- ≥ 1 → **混合模式**，派工分工依 `references/agent_routing.md` §2。
- 把每個 executor 的最終狀態寫進 `progress.md`「環境」欄，
  `broken` 者要一併寫下失敗原因（供下次接手者判斷是環境問題還是永久不可用）。
