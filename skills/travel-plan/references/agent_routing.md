# 可呼叫 agent 的偵測與依專長派工

> 本檔規範「有哪些 agent 可以用」與「哪種工作派給誰」。
> 模式（序列／平行／混合）與 Wave 依賴見 `references/workflow.md`；檢索規則見 `references/research_rules.md`。

---

## 1. 偵測：先確認誰真的可用

`SKILL.md` 啟動順序第 1 步的「子agent？」這一項，執行：

```bash
python3 scripts/detect_agents.py --self <主agent自己的子agent模型，如 sonnet>
```

無 Python 時走 `references/checklists/detect_agents.md`（等價的手動步驟）。

### 硬規則：binary 存在 ≠ 可用

**必須實際呼叫一次才算數。** 實測遇過 `copilot` 的 binary 確實在 PATH 上，
但那只是一支未安裝的 stub，執行後跳出 `Cannot find GitHub Copilot CLI ... Install? [y/N]`
的互動式安裝提示。若只用 `command -v` 判定，會把它當成可用的 executor 派工出去，
然後整個 Wave 卡在一個等待 y/N 輸入的提示上。

`detect_agents.py` 因此對每個 executor 做冒煙測試，並把輸出比對已知的失敗字串
（未安裝、未登入、未授權、eligibility check failed…），四種狀態的意義：

| 狀態 | 意義 | 可否派工 |
|---|---|---|
| `ready` | 冒煙測試通過，實際回應正確 | ✅ 可以 |
| `broken` | binary 在，但沒裝好／沒登入／權限不足 | ❌ 不可以，且要在 `progress.md`「環境」欄註明 |
| `absent` | 不在 PATH | ❌ 不可以 |
| `present_untested` | 只跑了 `--no-smoke` | ⚠️ **不可直接當成可用**，派工前補做冒煙測試 |

### 兩個實測踩過的坑

- **`--dangerously-skip-permissions` 可能被宿主的權限層攔下。** 在 Claude Code auto mode 下
  帶這個旗標呼叫 agy 會被 classifier 直接擋掉。派工指令保持最小旗標集，需要放寬權限時
  先問使用者。
- **`--add-dir` 可能觸發 eligibility 檢查失敗。** 實測 agy 帶 `--add-dir` 呼叫回
  `Eligibility check failed: UNAVAILABLE (code 503)`，拿掉即正常。
  冒煙測試通過但正式派工失敗時，**先把旗標減到最少重試一次**，再判定不可用。

---

## 2. 依專長派工

### 實測觀察到的差異

2026-09-10 以同一份查證任務（5 項韓國旅遊事實 ＋ 4 個網域可達性）同時派給
Claude Sonnet 子agent 與 agy（Gemini 3.8 Flash），主 agent 逐一開啟兩邊給的網址複驗，結果：

| 面向 | Claude Sonnet | Gemini Flash（agy） |
|---|---|---|
| **檢索韌性** | 弱。單一路徑 404 就放棄改引部落格，因此抄進錯誤票價（普通車報 5,350，官方 4,750） | **強**。同站換路徑找到官方票價頁 `/train/normal/fare`；找到 `egate.immigration.gov.tw`、`roc-taiwan.org` 等別人沒找到的官方來源 |
| **證據誠實度** | **高**。主動揭露「這頁只點名 Canada 沒有台灣」「這個更新日期可疑，疑似抓到今天日期」「日本側查不到就是查不到」 | 偏低。措辭傾向斷言，自我統計（「共 33 個網址，成功 22」）無從查證 |
| **遵守新規則** | 完全遵守。雙邊查找有做，查不到明說，不拿目的地國來源充數 | 完全遵守，且成功取得使用者所在國側官方來源 |
| **被複驗結果** | 引用的來源全部屬實，對來源限制的描述全部正確 | 引用的 4 個關鍵來源全部屬實、對題、確為官方 |

**結論**：兩者是互補而非優劣。Gemini Flash 適合「去挖」，Claude 適合「去驗」與
「需要嚴謹標註不確定性」的工作。

### 派工對照表

| 工作性質 | 首選 | 理由 |
|---|---|---|
| **09 素材庫的大量檢索**（景點、美食、來源蒐集） | Gemini Flash（agy） | 量大、需要韌性、錯了有 `validate_materials.py` 把關 |
| **02 通關／03 保險／11 緊急的官方來源挖掘** | Gemini Flash（agy）挖 → **主 agent 逐條複驗** | 這三個主題「出事沒人能負責」（§7），挖掘要韌性，但結論不能只靠挖的人自述 |
| **需要精確標註 `[待確認]` 的收斂工作** | Claude Sonnet 子agent | 誠實度高，不會把證據不足寫成肯定句 |
| **跨主題呼應檢查、Wave 收斂** | 主 agent 自己 | 需要全局 context，不可外包 |
| **最終複驗與去識別化把關** | 主 agent 自己 | 見下方硬規則 |

### 硬規則：來源必須複驗，不得採信 executor 自述

**任何 executor 回報的來源，主 agent 都必須自己開過才能寫進成品。**
特別是：

1. **自我統計一律不採信。** 「我試了 N 個網址、成功 M 個」這種數字無法查證，
   不得寫進 `progress.md` 或 TEST_REPORT 當作事實。
2. **02/03/11 三個最嚴格主題：逐條複驗，不抽驗。** 其餘主題至少抽驗
   每個 executor 的 2 條來源；抽驗發現任一條不實，該 executor 本輪所有來源全部重驗。
3. **複驗要驗三件事**（同 `research_rules.md` §2）：連得上、內容相符、是深層頁。
   實測抓到過「引用的官方網址根本不含它掛在下面的數字」
   （`airportrailroad.com/intro` 是動態訂票介面，被拿來當票價來源）。

### 派工指令必須包含的內容

子 agent 一旦派出即為非互動式（`workflow.md` §平行模式派工前必須問完），因此指令要自帶：

- 該主題的 `references/sections/0X_*.md` ＋ `references/research_rules.md` 路徑；
- `trip_context` 中該主題需要的欄位（**含 `origin`——雙邊官方來源規則要用**，見 §2.4）；
- 明確的回報格式：每項結論配「完整網址／來源側／tier／頁面日期／是否實際開啟」；
- 「查不到就寫查不到，不准編造網址、不准拿其他來源充數」；
- 「不要再往下派子 agent」（避免失控 fan-out）；
- 隱私要求：`private/` 內容不得寫入回報（見 `references/privacy.md`）。

---

## 3. 無任何 executor 可用時

`detect_agents.py` 回報 `ready_count: 0` → 走序列模式，在 `progress.md`「環境」欄
註明「無可用子agent，序列模式」。這不是降級失敗，是 `references/portability.md`
明列的正常路徑之一。
