# 可攜性：環境能力自檢與降級路徑

> 對應計畫書 §2 全部。本檔是 `SKILL.md` 啟動流程第 1 步「環境能力自檢」的完整規格。

## 為什麼要自檢而不是推斷

**能力要偵測，不能從「使用哪個產品」推斷。** 同一個產品在不同方案、不同設定、不同作業系統下能力都不同——例如 claude.ai 的自訂 Skill 需要 Pro/Max/Team/Enterprise 且啟用 code execution 才有程式執行能力；Claude Code 這類 CLI 場景反而是 Python 最不保證的一種（使用者本機可能沒裝、或裝了不在 PATH）。因此每次啟動都要**實測**，不得假設。

## 五項關鍵能力

| 能力 | 用途 | 偵測方式 | 缺席時的降級 |
|---|---|---|---|
| **網頁搜尋／抓取** | 全部檢索主題的基礎 | 檢查本次對話是否有可用的搜尋/抓取工具 | **唯一的硬需求**。沒有就無法執行，`SKILL.md` 啟動時明說並中止，不進入後續步驟 |
| **檔案讀寫** | 產出多份 md／JSON | 檢查本次對話是否有可用的檔案讀寫工具 | 幾乎所有宿主都有；真的沒有 → 改為對話輸出全文內容，請使用者自行複製存檔 |
| **程式執行（且有 Python 3）** | 跑校驗與渲染 script | 見下方「程式執行要拆成兩個問題」 | 改用 `references/checklists/` 的等效 md checklist，由 agent 手動執行 |
| **子 agent 派發** | 平行模式 | 檢查本次對話是否有可用的子 agent／task 派發工具 | 不問「要不要平行」，直接走序列模式 |
| **真人使用者在線** | 能不能問問題、能不能做人工確認 | 本次是被真人直接對話觸發，還是被另一個 agent／排程／批次呼叫？後者一律視為無真人 | 見下方「無真人使用者」專節——不是降級效率，是改變流程 |
| **git** | 進度可回退、commit 留痕 | 嘗試 `git status`（在專案目錄下），或檢查是否有版本控制相關工具 | 改用 `progress.md` 內建的「變更紀錄」區塊記錄每次更動 |

## 程式執行要拆成兩個獨立問題

這是最容易搞錯的一點，不能當成單一布林值：

1. **這個宿主有沒有把程式執行工具開給這次對話？**
   - claude.ai：自訂 Skill 需要 Pro/Max/Team/Enterprise 方案且啟用 code execution；免費方案或未啟用時，skill 的 script 完全跑不動。
   - ChatGPT：需要 Data Analysis 可用的方案。
   - Gemini：需要 code execution 工具啟用。
2. **script 是在哪台機器上跑？**
   - 雲端沙箱（claude.ai / ChatGPT.com / Gemini App）：容器裡是完整 CPython，標準庫齊全。
   - 使用者自己的電腦（Claude Code、Codex CLI、Gemini CLI 等本機 CLI）：**不保證裝了 Python**。

**因此啟動自檢必須實際驗證，而不是推斷**：

1. 嘗試執行 `python3 --version`。
2. 失敗則再嘗試 `python --version`。
3. 兩者皆失敗，或本次對話根本沒有程式執行工具可用 → 判定為「無程式執行能力」，全程走 `references/checklists/` 後備路徑，並在 `progress.md` 記錄「本次以 checklist 校驗」。
4. 成功 → 判定為「有程式執行能力」，可使用 `scripts/*.py`；但仍要遵守「script 失敗不得中斷流程」的鐵則（見下）。

## 各項能力缺席時的降級路徑（逐項展開）

### 無網頁搜尋／抓取
唯一硬需求。`SKILL.md` 啟動流程第 1 步偵測到此能力缺席時，直接告知使用者「目前環境無法搜尋或抓取網頁資料，無法執行旅遊規劃所需的資訊查證，本次任務中止」，不進入後續任何步驟。

### 無檔案讀寫
改為在對話中直接輸出完整內容（不省略、不摘要），並明確提示使用者「請自行複製以下內容另存為 `{建議檔名}`」。每個主題產出後都要這樣提示一次，因為沒有檔案系統代表無法用 `progress.md` 累積接手包，使用者是唯一的持久儲存。

### 無程式執行 / 無 Python 3
全程改用 `references/checklists/validate_materials.md`、`references/checklists/scrub_check.md` 等 md 後備，由 agent 依編號步驟手動執行機械性檢查（計數、比對日期、字串搜尋）。三條鐵則（見 §程式部分的鐵則）保證這條路徑永遠等價可行：
1. 沒有一支 script 是必要路徑。
2. script 失敗不得中斷流程，退回 checklist 並記錄。
3. script 只做校驗與格式轉換，不做檢索與判斷，因此 agent 手動做也不會漏掉需要判斷的部分。

### 無子 agent 派發能力
以 `scripts/detect_agents.py`（或 `references/checklists/detect_agents.md`）實測判定，**不得只用 `command -v` 判斷**——binary 存在可能只是未安裝的 stub。`ready` 數為 0 時，不在啟動流程第 5 步問「要平行還是序列」，直接視為序列模式，寫入 `progress.md`「環境」欄（`broken` 者要一併記下失敗原因）。依專長派工見 `references/agent_routing.md`。

### 無 git
不執行任何 `git commit`。改為每完成一個主題，在 `progress.md` 的「變更紀錄」區塊新增一行時間戳記＋摘要（格式見 `references/progress_protocol.md`）。無 git 環境下，`private/` 資料夾仍要遵守隱私分層規則（見 `references/privacy.md`），只是靠人工紀律而非 `.gitignore` 強制。

### 無真人使用者（被其他 agent 呼叫、排程執行、批次跑）

啟動流程有三個步驟預設有真人在線，無真人時**不得假裝問過、也不得靜默略過**：

| 原步驟 | 無真人時怎麼做 |
|---|---|
| **第 2 步 引導式提問** | 不能問。只能用已提供的檔案與 `trip_context` 推斷，所有推斷值一律寫進 `inferred_fields` 與 `progress.md`「待覆核的推斷值」 |
| **第 3 步 目的地門檻** | 抽不到目的地時**照樣中止**，但把固定句寫進最終回報而不是丟給對話。這一條不因無真人而放寬——目的地是唯一硬需求 |
| **第 4 步 trip_context 人工確認** | 人工關卡**不能取消，只能延後**。做法：正常產出 `trip_context.json`，在 `progress.md` 開一段「⚠ 尚未經人工確認」列出所有推斷值與去識別化結果，並在最終回報的**第一項**標明「這份 trip_context 尚未經人工覆核」 |
| **第 5 步 平行/序列詢問** | 不問。有子 agent 能力就走混合模式，沒有就走序列，並在 `progress.md`「環境」欄註明「無真人使用者，模式由 agent 自行決定」 |

**額外兩條硬規則**：

1. **無真人時不得執行 `git commit`。** commit 前必須先過 `trip_context` 的人工關卡（見 `references/privacy.md` 執行機制第 2 點），關卡沒過就不能把去識別化結果寫進版控。改為把變更留在工作區，並在回報中說明「待人工確認後再 commit」。
2. **序列模式的 context 清空指示改為回報內容。** 沒有真人可以執行 `/clear`，所以不要輸出那段對使用者的指示；改成在 `progress.md` 交接事項寫清楚下一階段的起點，讓呼叫方決定要不要續跑。

## 安裝與散佈：三種環境的安裝方式

SKILL.md 資料夾格式已是跨廠商標準（Anthropic 於 2025-12-18 開放為公開標準，發佈於 agentskills.io，OpenAI／Google 等約 32–40 個工具採用同一規格）。**格式已標準化，但 script 的執行環境完全沒有統一標準**——CLI 型工具在使用者本機跑，消費端網頁在各家雲端沙箱跑，容器與預裝套件每家不同且可能隨時改變。

| 環境 | 安裝方式 |
|---|---|
| **Claude Code / 其他支援 Agent Skills 的 CLI** | 把 `skills/travel-plan/` 複製或 symlink 到該工具的 skills 目錄（Claude Code 是 `~/.claude/skills/`） |
| **claude.ai 網頁／桌面版** | 打包 zip 上傳：`cd skills && zip -r travel-plan.zip travel-plan`。**需 Pro/Max/Team/Enterprise 方案且已啟用 code execution 才能使用 script 加速；未啟用時仍可用，只是全程走 checklist 後備** |
| **其他支援 SKILL.md 規格的宿主**（ChatGPT、Gemini CLI 等） | 依該工具文件把 `skills/travel-plan/` 資料夾提供給宿主；skill 資料夾自我完備，不依賴外部路徑 |

**skill 資料夾必須自我完備**——不得引用資料夾外的檔案，這是網頁版上傳能成立的前提。通用旅遊知識的骨架模板因此放在 skill 內 `templates/knowledge/`，而不是 skill 外部的共用目錄。
