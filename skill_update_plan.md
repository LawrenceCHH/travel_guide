# travel_guide → `travel-plan` Skill 改造計畫（v2・可攜版）

> 制定：2026-09-09 ｜ v2 修訂：2026-09-09（新增可攜性目標、隱私分層、程式方案）
> 需求來源：`../travel/初步規劃方法.md`
> 現況基準：本 repo 現有的 `prompt_generate_trip.md` / `prompt_update_trip.md` / `orchestrator/` / `travel_config_template.yml` / `travel_template.md` / `travel_general_mindset.md`
> 本檔是**計畫書**。實作開始後，進度由各趟旅程的 `progress.md` 與 §14 驗收表追蹤。

---

## 0. 定案

| 決策 | 結論 |
|---|---|
| 交付形態 | 轉型為 **Agent Skill**：`skills/travel-plan/`（SKILL.md + references/ + templates/ + scripts/），觸發 `/travel-plan` |
| **可攜性（v2 新增・最高約束）** | **任何人、任何環境都能用**：Claude Code、claude.ai 網頁/桌面版、其他支援 Agent Skills 的宿主。skill 資料夾必須**自我完備**，功能依環境能力**優雅降級**，不得因缺少 git／子 agent／程式執行而無法使用 |
| 素材格式 | **JSON 存素材，md 存成品**。選 JSON 而非 YAML 的理由見 §11.2；輸出約定見 §7.2 |
| 程式語言 | **Python 3，只用標準庫**；所有 script 都是**可選加速器**，每支都有等效的 md checklist 後備（見 §11） |
| 舊資產 | 雙軌 prompt 收斂為單一流程；**現有 repo 內容整批移入 `archive/`** |
| **隱私（v2 新增）** | **使用者提供的原始資訊不進版控**；agent 產生去識別化的 `trip_context.json` 才進版控（見 §5） |
| 與 travel 部落格 | 職責分離。travel_guide 產 md，之後由使用者選擇搬哪幾份進部落格，不做自動化 |
| Phase 3 驗收樣本 | 使用者本機的一份真實行程草稿（**不進版控，本檔不記載其內容**）。它同時具備紅眼班機抵達與回程當日下午起飛兩種極端，適合驗證首尾 buffer |

---

## 1. 現況與新架構的差距

### 1.1 現有資產的價值（必須被繼承，不能重寫掉）

舊 prompt 裡有幾塊是踩過坑才長出來的，改造時**原樣搬進新 references**：

- **目的地門檻檢查**：`trip_route` 無法辨識目的地時輸出固定句並中止，且 orchestrator 版特別註明「必須在派工前擋下，因為派工後即為非互動式，沒機會再問使用者」。
- **引用規範**：深層連結（去掉 domain 後路徑不可為空）＋ `[文章標題 - 作者/站名](網址)` ＋ 禁止自行拼湊路徑 ＋ 必須是搜尋/抓取實際回傳的網址。
- **逐一開連結驗證**三件事：回傳成功、內容相符、是深層文章頁；不通過就標 `[待確認：連結無法驗證]`。
- **`[待確認：原因]` 註記規範**：查不到就標記，嚴禁編造。
- **留空即預設**的設定哲學：填越少 agent 補越通用，缺欄位不中斷流程。
- **美食硬約束**：類別覆蓋、跨日反重複（同一主食類型全書最多 2 次）、每家補齊「價位帶／招牌菜／為何適合此同伴」、當地人 vs 觀光客雙視角。
- **同伴友善度評分（5 星）與雷區警示**。
- **通用心法**（`travel_general_mindset.md`）：洋蔥式穿搭、打包清單、保險索賠黃金清單、支付安全守則、長輩孩童照護、通用登機流程。幾乎可直接變成新架構的「通用旅遊知識」層。

### 1.2 新架構要求、但現有沒有的

| 新要求 | 現況 |
|---|---|
| 設定檔用 md 問卷 | 現在是 `travel_config.yml` |
| 每主題獨立一個 md 檔 | 現在全部塞進單一 `travel_{目的地}.md` |
| 交通資訊（在地交通卡／計程車防詐／交通 App） | 只有「機場→市區接駁」 |
| 當地習慣（獨立主題、含遊客特別注意事項） | 有一小節，深度不足 |
| 景點/美食**素材庫**與**行程安排**分離 | 混在同一章，素材無法重組 |
| 一次產出 **3 種行程方案** | 只產 1 套 |
| 半天為單位、大區域層級呈現 | 已是半日制，但缺區域層級 |
| `progress.md` 進度／checklist／交接 | 沒有 |
| 進度更新即 commit | 沒有 |
| 序列模式的記憶體清空策略 | 沒有 |
| 啟動時詢問平行/序列 | 靠「選哪個 prompt 檔」硬分兩套 |
| **跨宿主可攜** | 舊 orchestrator 明文要求「需可派發子 agent 的框架」，等於在網頁版直接不可用 |
| **原始資料不進版控** | 沒有隱私分層概念 |

### 1.3 新架構「漏掉」而舊架構有的（要補回去）

初步規劃的主題清單少了三塊，但它們都是舊版已驗證有用、風險又最高的：

1. **網路與漫遊方案**（eSIM / 實體 SIM / WiFi 分享器 / 電信商漫遊）
2. **免稅與退稅**
3. **緊急應變**（報警/救護熱線、駐外館處、可英文或中文就醫的醫院）— 出事沒人能負責，優先度最高

**➜ 主題數由 8 補回 11。**

---

## 2. 可攜性目標與環境分級（v2 核心）

### 2.1 目標

這份 skill 的使用者不會只有 Claude Code。有人會在 claude.ai 網頁版上傳 skill 使用，有人可能沒有程式執行環境。因此：

> **能力偵測 → 優雅降級**：skill 啟動時先判定當前環境能力，據此決定走哪條路徑，並把結論寫進 `progress.md`。**任何一項能力缺席，都只降低效率或自動化程度，不能讓流程中斷。**

### 2.2 五項關鍵能力

**能力要偵測，不能從「使用哪個產品」推斷**——§2.6 的查證顯示，同一個產品在不同方案、不同設定、不同作業系統下能力都不同。

| 能力 | 用途 | 缺席時的降級 |
|---|---|---|
| **網頁搜尋／抓取** | 全部檢索主題的基礎 | **唯一的硬需求**。沒有就無法執行，SKILL.md 啟動時明說並中止 |
| **檔案讀寫** | 產出多份 md／JSON | 幾乎所有宿主都有；真的沒有 → 改為對話輸出，使用者自行存檔 |
| **程式執行（且有 Python 3）** | 跑校驗與渲染 script | 改用等效的 md checklist 由 agent 手動執行（§11.3） |
| **子 agent 派發** | 平行模式 | 不問「要不要平行」，直接走序列 |
| **git** | 進度可回退 | 改用 `progress.md` 內建的變更紀錄區塊 |

### 2.3 「程式執行」這一項要拆成兩個獨立問題

這是查證後最反直覺的一點，原本 v2 把它當成一個布林值，是錯的：

1. **這個宿主有沒有把程式執行工具開給這次對話？**
   - claude.ai：自訂 Skill 需要 **Pro/Max/Team/Enterprise 且啟用 code execution**；免費方案或未啟用時，skill 的 script 完全跑不動。
   - ChatGPT：需要 Data Analysis 可用的方案（免費層是否可用**查無官方一手確認**，二手來源互相矛盾）。
   - Gemini：需要 code execution 工具啟用。
2. **script 是在哪台機器上跑？**
   - **雲端沙箱**（claude.ai / ChatGPT.com / Gemini App）：容器裡是完整 CPython，標準庫自然齊全。
   - **使用者自己的電腦**（Claude Code、Codex CLI、Gemini CLI）：**不保證裝了 Python**。Windows 使用者常見沒裝、或裝了不在 PATH。Anthropic 官方文件自己承認這個落差。

> **對本計畫的直接修正**：v2 原本假設「Claude Code 這類 CLI = 一定有程式執行」是**錯的**。CLI 場景反而是 Python 最不保證的一種。啟動自檢必須實際確認 `python3` 可執行，而不是從宿主類型推斷。

### 2.4 對設計的三個硬性影響

1. **skill 資料夾必須自我完備**——不得引用資料夾外的檔案。原 v1 把 `knowledge/` 放在 skill 外面是錯的，網頁版上傳時那些檔案不會跟著走。改為：**通用知識的骨架模板放 skill 內 `templates/knowledge/`**（只有結構、沒有事實，見 §6.1），工作區的 `knowledge/` 降為有持久儲存時的填充結果快取。
2. **`progress.md` 必須足以獨立恢復**——網頁版跨對話沒有持久檔案系統，使用者關掉視窗就沒了。所以 progress.md 不只是進度表，它是**接手包的目錄**，agent 每階段結束要明確告訴使用者「請保存這幾個檔案，下次開新對話時上傳」。
   *附帶好處*：這與 CLI 序列模式「清空 context 後重讀 progress.md 續跑」是**同一個需求**，一套設計服務兩種環境。
3. **平行處理不是預設也不是必要**——它是「具備子 agent 派發能力」時的加速選項。SKILL.md 的啟動流程必須先自檢，**確認有子 agent 能力才問這一題**，否則直接走序列（避免對網頁版使用者問一個他無法選的問題）。

### 2.5 安裝與散佈：SKILL.md 已經是跨廠商標準

**這是查證後最好的消息，它讓「任何人任何環境都能用」在格式層直接成立**：

- Anthropic 於 **2025-12-18** 把 Agent Skills 規格開放為公開標準，發佈於 **agentskills.io**，由 Agentic AI Foundation 治理。
- OpenAI 在 **48 小時內**讓 ChatGPT 與 Codex CLI 支援同一份 SKILL.md；Google Gemini CLI 也在採用名單內。
- 到 2026 年，約 **32–40 個工具**吃同一份規格，含 VS Code/Copilot、Cursor、Goose、JetBrains Junie、AWS Kiro、Databricks、Snowflake 等。

來源：[Anthropic - Introducing Agent Skills](https://www.anthropic.com/news/skills)、[agentskills/agentskills 規格](https://github.com/agentskills/agentskills)、[Simon Willison, 2025-12-12](https://simonwillison.net/2025/Dec/12/openai-skills/)、[Simon Willison, 2025-12-19](https://simonwillison.net/2025/Dec/19/agent-skills/)

**所以要嚴格區分兩件事**：

| 層次 | 現況 |
|---|---|
| **格式**（SKILL.md 資料夾 + frontmatter） | **已是跨廠商標準**，幾乎沒有例外 |
| **script 的執行環境** | **完全沒有統一標準**。CLI 型工具在使用者本機跑、消費端網頁在各家雲端沙箱跑，容器、預裝套件、網路權限每家都不同，且可能隨時改變 |

**安裝方式**：
- **Claude Code / 其他 CLI**：`skills/travel-plan/` 複製或 symlink 到該工具的 skills 目錄（Claude Code 是 `~/.claude/skills/`）。
- **claude.ai 網頁／桌面版**：打包 zip 上傳（`cd skills && zip -r travel-plan.zip travel-plan`）。**需 Pro/Max/Team/Enterprise 且已啟用 code execution。**
- **SKILL.md frontmatter** 必須有 `name` 與 `description`，description 寫滿觸發語（旅遊規劃、行程安排、travel plan、itinerary…），這是宿主決定何時載入 skill 的唯一依據。
- skill 資料夾控制體積：SKILL.md 精簡（目標 300 行內），主題規格分散在 references 按需讀取。

### 2.6 執行環境查證結果（2026-09-09）

| 平台 | 程式執行 | 語言 | 裝套件 | PyYAML 預裝 |
|---|---|---|---|---|
| **claude.ai** | Code Execution Tool（2025-11-05 取代原本瀏覽器內 JS 的 Analysis tool） | **Python + Bash**，Linux x86_64 / gVisor | Free/Pro/Max 預設可連網（可關）；Team/Enterprise 預設僅套件管理器或全關；API 介面**完全無網路** | **不在官方預裝清單** |
| **ChatGPT** | Data Analysis（2026-01 擴充為 Containers） | Python 為核心，另支援 Node/Bash/Ruby/Go/Java 等 | 沙箱無直接外網，但可經內部鏡像 `pip install` | 未列出，**查不到** |
| **Gemini** | Code Execution tool | **只有 Python**（官方原文：只能執行 Python） | **明確禁止安裝任何套件** | 未列出 |

主要來源：[Claude Platform Docs - Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)、[Claude Platform Docs - Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)、[support.claude.com - Create and edit files](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)、[Gemini API - Code execution](https://ai.google.dev/gemini-api/docs/code-execution)、[Simon Willison, 2026-01-26 - ChatGPT Containers](https://simonwillison.net/2026/Jan/26/chatgpt-containers/)

**查不到、需保守處理的缺口**：ChatGPT Data Analysis 免費方案的真實可用範圍（官方頁面擋爬蟲，無法一手驗證）；Gemini 網頁消費端 App 是否與 API 文件描述的沙箱一致；三家的預裝套件清單都非正式保證，隨時可能變。

---

## 3. 目標形態：目錄結構

```
travel_guide/
├── README.md                        # 安裝（三種環境）、使用、模式取捨
├── skill_update_plan.md             # 本檔
├── .gitignore                       # ★ 排除所有原始個資（見 §5）
├── archive/                         # 舊資產整批封存，只供引用
│   ├── README.md                    # 封存 banner：此目錄不描述現況
│   ├── prompt_generate_trip.md / prompt_update_trip.md / orchestrator/
│   ├── travel_template.md / travel_config_template.yml / travel_general_mindset.md
│   ├── travel_韓國首爾*.md / Korean/ / index.html / plan.md / verification_report.md
│   └── .claude|.agents/skills/      # 與旅遊無關的設計類 skill，一併封存
│
├── skills/travel-plan/              # ★ 交付主體・自我完備・可單獨打包上傳
│   ├── SKILL.md                     # frontmatter + 環境自檢 + 啟動對話 + 階段機 + 路由表
│   ├── references/
│   │   ├── workflow.md              # 序列/平行/混合三模式與 Wave 調度
│   │   ├── progress_protocol.md     # progress.md 格式、交接、接續包、commit
│   │   ├── privacy.md               # ★ 抽象化規則表、什麼進版控
│   │   ├── research_rules.md        # 檢索、來源分級、引用、查證、待確認註記
│   │   ├── portability.md           # ★ 能力自檢與各項降級路徑
│   │   ├── checklists/              # ★ script 的 md 後備版（無 Python 時用）
│   │   │   ├── validate_materials.md
│   │   │   └── scrub_check.md
│   │   └── sections/                # 每個主題一份產出規格
│   │       ├── 01_flight_stay.md    ├── 07_tax_refund.md
│   │       ├── 02_immigration.md    ├── 08_local_customs.md
│   │       ├── 03_insurance.md      ├── 09_materials.md
│   │       ├── 04_connectivity.md   ├── 10_itinerary.md
│   │       ├── 05_transport.md      └── 11_emergency.md
│   │       └── 06_payment.md
│   ├── templates/
│   │   ├── knowledge/                   # ★ 通用知識「骨架」：只有結構與 {{查最新}} 佔位
│   │   │   ├── clothing_by_climate.template.md
│   │   │   ├── packing.template.md
│   │   │   ├── pre_trip_checklist.template.md
│   │   │   ├── insurance_claim.template.md
│   │   │   ├── payment_safety.template.md
│   │   │   └── companion_care.template.md
│   │   ├── trip_profile.template.md     # 選填輔助問卷（非主要入口，見 §4.1）
│   │   ├── trip_context.schema.json     # ★ 去識別化脈絡檔的 schema
│   │   ├── progress.template.md
│   │   ├── spots.schema.json / food.schema.json
│   │   └── section.template.md          # 成品共用檔頭（含 last_verified）
│   └── scripts/                     # 全部 Python 3 stdlib-only，全部可選
│       ├── validate_materials.py
│       ├── render_materials.py
│       └── scrub_check.py           # ★ 個資外洩掃描
│
├── knowledge/                       # 骨架填充後的快取，帶 last_verified，6 個月內複用
└── trips/                           # 每趟旅程
    └── 2026-10-seoul/
        ├── private/                 # ★ .gitignore，永不進版控
        │   ├── input/*              #   使用者原始輸入（任何格式，含航班號、訂位代號、姓名）
        │   └── personal/*.md        #   個人化成品（含飯店名與航班的最終版）
        ├── trip_context.json        # ★ 去識別化後，進版控
        ├── progress.md              # 進版控
        ├── materials/{spots.json, food.json}   # 進版控
        └── plan/01_*.md … 11_*.md   # 進版控（只引用 trip_context 層級資訊）
```

**為什麼 SKILL.md 只放流程**：skill 主檔每次觸發都整份載入 context。把 11 個主題的檢索規則全寫進去，等於每趟旅程、每個子 agent 都付一次全額。改成「主檔放路由 + references 按需讀取」，序列模式每階段只讀自己那份，平行模式每個子 agent 只帶自己那份 + 共用的 `research_rules.md`。

---

## 4. 使用者資訊：任意輸入 → 去識別化 JSON

### 4.1 三種取得方式（依優先序）

1. **使用者已有檔案**（預設路徑）——任何 agent 讀得懂的格式：md、txt、訂房確認信、行事曆匯出、截圖、docx、pdf 都行。agent 直接讀並抽取。
   *這條之所以是預設，是因為真實使用者手上通常已經有東西*——實測樣本就是典型的混合形態：半結構的行程草稿 + 整段貼上的訂房確認信 + 手打的班機時刻，三種來源混在同一個檔案裡。
2. **沒有檔案 → agent 引導式提問**。一次問一批（3~5 題），不逐題來回；先問決定性的（目的地、日期、班機時刻、住宿區位），其餘用預設。每題附上「不回答會怎樣」。
3. **什麼都不想給** → 除目的地外全部走預設推斷，並在 `progress.md` 全部標記為待覆核。

**`trip_profile.template.md` 因此降級為選填輔助**，給偏好自己填表的人用，不再是主要入口。

### 4.2 agent 必須抽出的欄位

| 欄位 | 抽不到時的行為 |
|---|---|
| 目的地 | **唯一硬停**：輸出固定句並中止 |
| 旅遊起訖日期 | 反問（影響季節、資訊時效、天數） |
| 出發/回程時刻與機場航廈 | 推斷常見班次，標記待覆核（影響首尾 buffer） |
| 航空公司 | 推斷該航線主流航司，標記待覆核（影響行李規範） |
| 住宿區位 | 推斷該目的地常見住宿區，標記待覆核（影響景點分區） |
| 成員結構 | 預設「一般成人旅客」，仍產友善度評分但不做特殊加權 |
| 旅行風格、指名景點、美食偏好、預算、電信商、來源偏好 | 全部走既有的「留空即預設」規則，不中斷 |

### 4.3 為什麼中介產物是 JSON

抽取結果不留在散文裡，而是整理成 **`trip_context.json`**：

- **下游 11 個主題都要讀它**。固定欄位不會讀歪；散文每次讀都要重新理解一次。
- **去識別化檢查更可靠**：比對「有哪些欄位、值是什麼」，比在散文裡抓漏網的姓名或訂位代號穩得多。
- **與素材庫同格式**，整套 skill 只需要一條解析路徑。
- 人要看的版本由 `render` 產生成 md，不影響閱讀。

原始輸入（含個資）留在 `private/`，見 §5。

## 5. 隱私分層：什麼進版控（v2 核心）

### 5.1 原則

> **版控的是「知識」，不版控的是「身分」。**
> 使用者提供的原始資訊一律不進版控；agent 產生的**去識別化 `trip_context.json`** 才進版控。所有下游產出只引用 `trip_context`，不回填原始值。

### 5.2 去識別化規則表

> 以下欄位值皆為**虛構示意**。真實行程檔留在使用者本機，本計畫書本身也適用同一條規則——**不記載任何真實訂位資訊**。

| 原始欄位（範例值） | 進版控的形式 | 理由 |
|---|---|---|
| 訂房確認號 `<8 位數字>` | **刪除** | 可被用來查詢或變更他人訂房 |
| 訂房人姓名 | **刪除**（或「成員 A」） | 直接識別 |
| 航班號（去程／回程） | **刪除** | 可反查訂位；規劃本身用不到 |
| 起降時刻（如 `01:25→05:00`、`16:10`） | **保留** | 首尾 buffer 計算的必要輸入 |
| 航空公司 | **保留** | 查行李規範必需，不具識別性 |
| 機場含航廈 `TPE T1` / `ICN T2` | **保留** | 通關流程必需 |
| 飯店名 + 門牌地址 | **改為「區域 + 最近車站」** | 規劃只需要區位；名稱門牌可定位居住地 |
| 房型與訂單人數 | **改為結構描述**（如「4 位成人、1 房」） | 規劃需要的是限制條件不是訂單 |
| 聯絡方式、Email、電話 | **一律刪除** | — |

### 5.3 `trip_context.json` 產出範例（**虛構資料**，僅示意結構）

```json
{
  "version": 1,
  "destination": "韓國首爾",
  "dates": {"start": "2027-04-08", "end": "2027-04-12", "nights": 4, "season": "春"},
  "arrival":   {"date": "2027-04-08", "time": "05:00", "airport": "ICN", "terminal": "T2", "carrier": "A 航空"},
  "departure": {"date": "2027-04-12", "time": "16:10", "airport": "ICN", "terminal": "T2", "carrier": "B 航空"},
  "origin":    {"airport": "TPE", "terminal": "T1"},
  "stay":      {"area": "市中心商圈一帶", "nearest_station": "主要轉乘站（1／2 號線）", "checkin": "15:00"},
  "party":     {"adults": 4, "children": 0, "rooms": 1, "mobility_notes": null},
  "style":     {"pace": null, "interests": []},
  "named_musts": ["古宮與周邊韓屋聚落", "傳統市場", "河濱夜遊", "文青商圈"],
  "named_undecided": ["觀景塔", "大學商圈"],
  "derived_constraints": [
    "Day1 05:00 抵達為紅眼班機：可用時數長但體力低，且飯店 15:00 才能入住，需安排行李寄放與低強度行程",
    "Day5 16:10 起飛：回推報到時間，最晚 13:30 需離開市區，末半天實際可用約 3 小時",
    "一日包車行程屬必須事先預約項目"
  ],
  "inferred_fields": ["stay.area", "stay.nearest_station"],
  "provenance": "private/input/（使用者提供，不進版控）"
}
```

`derived_constraints` 是刻意保留的自然語言欄位——它裝的是**推論結果**（紅眼班機該怎麼排），不是個資，而且下游主題最需要的就是這幾句。`inferred_fields` 列出哪些值是推斷來的，直接餵給 progress.md 的待覆核區。

### 5.4 執行機制

1. `.gitignore` 加入 `trips/*/private/`。
2. agent 產出 `trip_context.json` 後，**第一次 commit 前必須讓使用者過目確認**——人工關卡，不可跳過。
3. `scripts/scrub_check.py`（有程式執行時）：從 `private/` 的原始輸入抽出專有字串（確認號、姓名、航班號、飯店名等 token），掃描所有**將進版控的檔案**是否含這些字串，命中即報錯。無程式執行時走 `references/checklists/scrub_check.md` 手動比對。
4. **個人化成品放 `private/personal/`**：使用者旅行時當然想看到飯店名與航班號。作法是 `plan/` 保持抽象可版控，agent 另外用 `plan/` + 原始輸入合成一份個人化版本放進 `private/personal/`，不進版控。
5. progress.md 一律只引用 trip_context 層級的值。

### 5.5 無 git 環境的隱私意義

網頁版沒有 git，但分層依然有價值：使用者會下載並可能分享 `plan/`，而 `private/` 明確標示為不可分享。skill 輸出「接續包」清單時要標明哪些可分享、哪些不可。

## 6. 兩層知識：通用（低頻）vs 行程（高頻）

### 6.1 通用旅遊知識層：**骨架，不是內容**

> **決策修正（v2.1）**：原本打算把舊 `travel_general_mindset.md` 的內容抽成六個「知識種子」隨 skill 散佈。**改為只散佈骨架模板，內容由 agent 依最新資訊現場產生。**

**為什麼改**：

1. **那份檔不是通用的，是「台灣出發」專屬的**——護照效期、外交部領事局補發、健保署自墊核退 6 個月期限、桃園機場流程、移民署 e-Gate 年滿 10 歲身高 120 公分。對非台灣出發的使用者不僅無用，還會**誤導**。
2. **它凍結了會過期的事實**：鋰電池 100Wh / 160Wh 規範、不便險延誤滿 4 小時起賠、健保核退期限。skill 一旦散佈出去就沒有更新路徑，這些數字會安靜地變舊。
3. **它自己的引用不合格**：實測該檔 12 個連結中 **9 個是網域根目錄**（`https://www.caa.gov.tw`、`https://www.nhi.gov.tw`、`https://www.immigration.gov.tw` …），只有 3 個是深層文章頁。**依本 skill 自己的引用規範，這份檔會被判不合格**——沒有理由把不合格的內容當成種子散佈出去。

**改成什麼**：`templates/knowledge/*.template.md`，每份骨架只定義三件事——

- **章節結構與必須產出的表格欄位**（例如穿搭表必須有「季節 × 氣候情境 → 內/中/外三層 + 必備配件」；物品表必須有「為什麼要帶／用途」欄）
- **必須回答的問題清單**（例如打包骨架要問：這個目的地電壓與插座型號？行動電源規範以哪國民航局為準？）
- **明確標記哪些格子是易變事實**，一律 `{{查最新：主題}}` 佔位，禁止骨架內寫死任何數字、金額、期限與網址

六份骨架：`clothing_by_climate` / `packing` / `pre_trip_checklist` / `insurance_claim` / `payment_safety` / `companion_care`。

**怎麼用**：agent 依 `trip_context` 的**出發國 × 目的地 × 季節 × 成員**填滿骨架，產出 `plan/00_general.md`，每個易變事實都要附深層來源連結與 `last_verified`。

**快取策略**：有持久檔案系統時，填好的結果存到工作區 `knowledge/{出發國}-{目的地區域}.md`，帶 `last_verified`，**6 個月內同組合直接複用**，只做季節與成員的裁剪，不重查。沒有持久儲存的環境每趟重新產生——多一次檢索，可接受。

舊的 `travel_general_mindset.md` 移入 `archive/`，作為**寫骨架時的參考素材**（它的分類邏輯與心法角度是對的，只有事實與引用不能用）。

### 6.2 行程資訊層 `trips/{trip}/plan/`

每主題一檔，**強制近一年資訊**（真的沒有才放寬到兩年，且必須在文中註明「來源為 N 年前」），每個段落對應可驗證的來源網址。

- **01 行程資訊**：班機/住宿整理成可查表，補「機場→住宿」與「住宿→機場」實際路線與預估時間，回推機場報到時間。**含「訂位與預約清單」**（見 §12）。
- **02 機場通關**：出發與抵達機場整合成一條 Step-by-Step，當作讀者沒出過國來寫；精簡但精準到「照著做一定過關」。**違禁品清單**與**行李規範**為必要段落。快速通關（Visit Japan Web / Q-Code / e-Arrival）逐國不同，必須查當年度最新。**每段強制對應來源網址。**
- **03 保險**：官方與部落客兩類來源分開列，對比 2~3 家方案的突發疾病醫療額度、班機延誤起賠時數與額度。**每段強制對應來源網址。**
- **04 網路與漫遊**：eSIM / 實體 SIM / WiFi 分享器 / 電信商漫遊四軌對比表 + CP 值推薦。
- **05 交通資訊**：(a) 落地到住宿的所有方案與部落客推薦；(b) 當地交通卡（T-money / Suica / Toss）申辦、儲值、**退卡**步驟；(c) 行程間移動手段；(d) 計程車注意事項與**防詐**；(e) 推薦交通 App/網站。
- **06 支付方式**：當地實際用什麼、台灣部落客怎麼說、申辦 Step-by-Step、**優缺點對比表格**並標明哪些偏當地人限定而非遊客可用。
- **07 免稅與退稅**：起徵門檻、店家即時退稅 vs 機場退稅 vs App 退稅、實際流程。
- **08 當地習慣**：通行方向、飲食與生活與購物習慣、社交禁忌、小費文化、**外國遊客特別容易踩的雷**（如語言差別定價）。
- **09 素材庫**：見 §7。
- **10 行程安排**：見 §8。
- **11 緊急應變**：報警/消防/救護熱線、駐外館處電話地址、可英文或中文就醫的醫院、護照遺失補辦、信用卡掛失。

**風險分級**：02 通關、03 保險、11 緊急這三塊「出事沒人能負責」，規格設為**最嚴格等級**——只採官方第一手來源，每條資訊後綴來源連結，不接受概括引用。

---

## 7. 素材庫：JSON

素材庫是「原始素材」，行程安排是「組合成品」。分離的價值：改行程不用重查素材，一份素材可組出 3 套行程。

**格式定案為 JSON**，理由見 §11.2（零依賴 + 不會像 YAML 那樣靜默誤判）。

### 7.1 Schema

`materials/spots.json`：
```json
{
  "version": 1,
  "destination": "韓國首爾",
  "last_verified": "2026-09-09",
  "areas": [
    {
      "id": "gyeongbok",
      "name": "景福宮・三清洞",
      "summary": "一句話描述這個大區域的性格",
      "nearest_station": "景福宮站 3 號線",
      "spots": [
        {
          "id": "gyeongbokgung",
          "name": "景福宮",
          "name_local": "경복궁",
          "category": "文化古蹟",
          "audience": ["tourist_must"],
          "why": "推薦理由，一到兩句",
          "duration_min": 120,
          "friendliness": {"score": 4, "notes": "石板路長、無遮蔽"},
          "open_hours": "09:00-18:00",
          "closed_on": "週二",
          "fee": "成人 3000 KRW",
          "booking_required": false,
          "rainy_day_ok": false,
          "sources": [
            {"title": "…", "site": "…", "url": "https://…/deep/path",
             "published": "2026-03-11", "tier": "official"}
          ]
        }
      ]
    }
  ]
}
```

`materials/food.json`：
```json
{
  "version": 1,
  "areas": [
    {
      "id": "gyeongbok",
      "picks": [
        {
          "id": "cafe_onion_anguk",
          "name": "Cafe Onion 安國店",
          "name_local": "카페 어니언 안국점",
          "category": "咖啡甜點",
          "audience": "tourist",
          "near_spot": "gyeongbokgung",
          "walk_min": 8,
          "price_band": "₩₩",
          "signature": "팡도르",
          "why": "推薦理由",
          "caution": "假日排隊 40 分以上，替代方案 O'sulloc",
          "sources": [{"title": "…", "site": "…", "url": "https://…",
                       "published": "2026-05-02", "tier": "blogger"}]
        }
      ]
    }
  ]
}
```

**列舉值**（JSON 沒有註解，因此合法值定義在 `references/sections/09_materials.md`，不寫在資料檔裡）：
- `spots.category`：`文化古蹟` `自然景觀` `購物商圈` `網美打卡` `體驗活動` `室內歇腳`
- `spots.audience`：`tourist_must` `local_favorite`（可並列）
- `food.category`：`正餐` `小吃` `咖啡甜點` `伴手禮`
- `food.audience`：`tourist` `local`
- `sources.tier`：`official` `platform` `blogger`

### 7.2 輸出約定（取代原本的「受限 YAML 子集」）

JSON 本身沒有歧義，但**diff 品質靠約定維持**——這一點是選 JSON 時要補回來的：

- **欄位順序固定**，依 schema 宣告順序輸出，不得因重新產生而重排
- **巢狀不超過 3 層**（root → areas → spots/picks → 物件欄位）
- `sources` 陣列**每個來源物件寫成一行**，減少改動時的行數擾動
- 縮排 2 空格，UTF-8，**不轉義非 ASCII**（`ensure_ascii=false`），中文與韓文直接可讀
- 檔尾保留換行
- 修改既有素材時**只動該筆物件**，不重排、不重新格式化整檔

這組約定寫進 `references/sections/09_materials.md` 當作 agent 的輸出契約，並由 `render_materials` 在寫檔時強制執行。

### 7.3 硬約束（由校驗執行）

1. 每個 area 的 `picks` 必須含**觀光客 3 家 + 當地人 3 家**，且類別橫跨至少 3 類。
2. 跨日反重複：同一主食類型全書最多出現 2 次。
3. 每筆必須有非空 `sources`，且 url 去掉 domain 後路徑不可為空。
4. `published` 距今超過 1 年要標記；超過 2 年判不合格。
5. 每個 area 至少 1 個 `rainy_day_ok: true` 的景點或歇腳處（供 Plan B）。
6. `food.near_spot` 必須存在於 `spots.json` 的同 area 中（參照完整性）。
7. 所有列舉欄位的值必須落在 §7.1 的合法值清單內。

## 8. 行程安排：3 套方案

前置條件：`09 素材庫` 與 `05 交通` 完成，且 trip_context 有出發/回程時刻。

1. **半天為單位**（上午／下午），**不列具體時間**。
2. 半天區塊內，景點與美食必須**鄰近**（步行 15 分或車程 10 分內）；日與日之間可拉遠。
3. **首尾強制 buffer**：依班機時刻扣掉通關/交通/報到，明確寫出「這個半天只剩 N 小時可用」，且只排低風險行程。
   *兩個必須寫進規格的極端案例*：清晨 05:00 抵達 → 可用時間長但飯店 15:00 才能 check-in、且旅客整夜未睡；回程日下午 16:10 起飛 → 末半天實際約 3 小時，只能安排住宿步行圈內、且不能寄不回來的行李。
4. **層級呈現**：大區域 → 區域簡述 → 區域美食推薦 → 區內景點 → 各景點旁步行可到的美食。
5. **產出 3 種方案**，每套標明「適合誰」。建議三軸：
   - A｜經典必去：一生一次該去的地標優先
   - B｜深度在地：當地人私房景點與巷弄美食優先
   - C｜輕鬆慢遊：每天景點數減半、移動最短、室內歇腳處密度最高
   若 trip_profile 的 C2 風格有勾選，第一套必須貼合該風格。
6. **每個半天配 1 個 Plan B**：下雨、公休、排隊過長的替代（從素材庫 `rainy_day_ok` 挑）。
7. 使用者沒提供風格與指名景點時，**以部落客實際走過的路線優先**（有實際體驗較不易出錯）。
8. **既有草稿優先串聯**：使用者若已給草稿（如實測樣本），三套方案都必須涵蓋草稿裡的指名點，差異體現在補洞的部分（如首爾塔、弘大要不要排、南怡島包車 vs 自行前往）。

---

## 9. 執行模式：先自檢，再詢問

### 9.1 啟動順序（順序不可調換）

```
1. 環境能力自檢 → 寫入 progress.md「環境」欄
     網頁搜尋？檔案讀寫？子 agent？git？
     程式執行 → **實測 `python3 --version`（失敗再試 `python --version`）**，不從宿主類型推斷
     └ 無網頁搜尋 → 明確告知使用者無法執行並中止
2. 取得使用者資訊（§4.1：讀既有檔案 ▸ 引導式提問 ▸ 全預設）
3. 目的地門檻檢查 → 無法辨識就輸出固定句並中止
4. 產出 trip_context.json → 請使用者確認去識別化結果
5. 【只有具備子 agent 能力時才問】要平行還是序列？
6. 建立 progress.md，開跑
```

第 5 步的位置很重要：**必須在派任何工之前**。承襲舊 orchestrator 的教訓——派工後即為非互動式，子 agent 沒機會問使用者，所有需要使用者決定的事必須在此之前一次問完。

### 9.2 三種模式

| 模式 | 說明 | 代價 |
|---|---|---|
| **序列**（無子 agent 時的唯一選項） | 單一 agent 逐主題執行 | 省 token；但 context 逐步膨脹，需定期清空並靠 progress.md 接手 |
| **平行**（具子 agent 派發能力時） | 主 agent 分波派工，同時深挖多主題 | 快；每個子 agent 各自載入 trip_context + 檢索規範，重複成本 ≈ 單份 × N |
| **混合**（有子 agent 時的預設推薦） | 檢索類主題平行，素材庫與行程安排序列 | 依賴結構決定的自然解，見下 |

### 9.3 依賴分析：為什麼不能全部平行

```
前置（主 agent 自己做，不需檢索）
  00 通用知識裁剪 ｜ 01 行程資訊整理

Wave 1（可完全平行，彼此不依賴）
  02 通關 ｜ 03 保險 ｜ 04 網路 ｜ 05 交通 ｜ 06 支付 ｜ 07 退稅 ｜ 08 當地習慣 ｜ 11 緊急
                            │
Wave 2（依賴 05 交通的區域可達性 + 01 的住宿區位）
  09 素材庫（景點 → 美食；美食必須等景點定了才算得出步行距離）
                            │
Wave 3（依賴 09 + 05 + trip_context 首尾時刻）
  10 行程安排（3 方案）
```

**跨主題呼應檢查**由主 agent 在收斂時做：推薦 App 是否呼應交通與支付章節、行程中的接駁是否與交通章節一致、素材庫的店家是否被行程實際用到。

### 9.4 序列模式的記憶體管理（現實限制要講清楚）

**agent 不能清空自己的 context**。序列模式的循環必須是：

```
讀 progress.md（含交接事項）
  → 執行 1 個主題
  → 寫成品 md
  → 更新 progress.md（勾 checklist、寫交接、記待確認）
  → 有 git 就 commit／沒有就更新 progress.md 的變更紀錄區塊
  → 對使用者說：「本階段完成。
     有持久檔案系統：請執行 /clear（或等效清空）後回覆『繼續』；
     網頁版：請下載接續包這幾個檔案，開新對話上傳後回覆『繼續』」
  → 新 context 重讀 progress.md → 下一階段
```

skill 必須把最後兩步寫成**對使用者的明確指示**，而不是假裝 agent 自己會清。使用者若不想中斷，退化成 context 持續膨脹，並在 progress.md 記錄此選擇。

---

## 10. `progress.md` 協議

### 10.1 格式

```markdown
# 2026-10-seoul 規劃進度

## 環境
- 宿主：Claude Code ｜搜尋 ✓ 檔案 ✓ 子agent ✓ git ✓ ｜Python 3.12.3（實測通過）
- 模式：混合（Wave 1 平行 / Wave 2-3 序列）
- 建立：2026-09-09 ｜ 最後更新：2026-09-09

## 待覆核的推斷值
- 住宿區位由飯店名推斷為「市中心商圈一帶」，請確認。

## Checklist
| # | 主題 | 狀態 | 產出檔 | 負責 | 最後更新 |
|---|---|---|---|---|---|
| 00 | 通用知識裁剪 | done | plan/00_general.md | main | 09-09 |
| 02 | 機場通關 | doing | plan/02_immigration.md | agent-2 | 09-09 |
| 09 | 素材庫 | blocked（等 05） | — | — | — |

## 交接事項（下一個 context 必須知道）
- 05 交通已確認機場快線 2026 改點，行程安排時末班車以 22:40 為準。
- 使用者草稿指名南怡島包車，三套方案都必須包含。

## 待確認清單（[待確認：...] 彙整）
- 02：ICN T2 快速通關 2026 新制官方公告未發布，暫引 2025 版並標記。

## 決策紀錄
- 09-09：美食素材改以 area_id 分組而非逐景點，因同區多景點會重複列同一家店。

## 接續包（無持久儲存時・下次開新對話請上傳）
- [可分享] trip_context.json / progress.md / materials/*.json / plan/*.md
- [不可分享] private/input/*（僅自己保存，不要貼進公開場合）

## 變更紀錄（無 git 時使用）
- 2026-09-09 14:20 完成 05 交通
```

### 10.2 更新與 commit 時機

- **序列**：每完成一個主題 → 更新 progress.md → commit。
- **平行**：主 agent 在派工前寫入本波計畫並 commit；每收到一個子 agent 回報就更新對應列並 commit。**子 agent 不直接寫 progress.md**（避免併發衝突），只回報。
- commit 訊息：`progress({trip}): {主題編號} {狀態}`，例 `progress(2026-10-seoul): 05 交通 done`。
- **commit 前必跑 scrub 檢查**（§5.4），確認沒有原始個資外洩。

---

## 11. 程式部分怎麼解決（v2 核心）

### 11.1 語言選擇：Python 3，只用標準庫（已查證）

依 §2.6 的查證結果：

| 選項 | 評估 |
|---|---|
| **Python 3 標準庫**（採用） | **三家消費端沙箱的最大公約數**——Gemini 只能跑 Python，claude.ai 是 Python + Bash，ChatGPT 以 Python 為核心。只用標準庫則無安裝步驟、無網路需求，在「明確禁止裝套件」的 Gemini 也能跑 |
| Node | Gemini **只能執行 Python**，直接出局；本機實測也是 `node: command not found` |
| 任何第三方套件（含 PyYAML） | **PyYAML 不在 Claude 官方預裝清單，Gemini 與 ChatGPT 的清單也查不到它**；Gemini 更是明確禁止安裝任何套件。且 **PyYAML 從來就不是標準庫**——這正好再次印證 §11.2 選 JSON 的決定 |
| 純 md 規則靠 agent 自查 | 每次自查燒 token 且容易漏。**降為無程式執行時的後備，不當主方案** |

#### 但「一定有 Python」本身不是安全假設

查證的結論是**有條件的「是」**，兩個條件都要處理：

1. **程式執行工具必須已被啟用**。claude.ai 自訂 Skill 需付費方案 + 啟用 code execution；ChatGPT 需 Data Analysis 可用的方案；Gemini 需啟用該工具。任何一個沒開，script 都跑不動。
2. **本機 CLI 場景不保證裝了 Python**。Claude Code / Codex CLI / Gemini CLI 的 script 是在**使用者自己的電腦**上跑，Windows 使用者常見沒裝 Python 或不在 PATH。**這是本計畫原本假設錯誤的地方**——CLI 反而是 Python 最不保證的環境。

**因此啟動自檢必須實際驗證，而不是推斷**：先嘗試執行 `python3 --version`（失敗再試 `python --version`），成功才走 script 路徑，失敗一律走 §11.3 的 md checklist，並在 `progress.md` 記錄「本次以 checklist 校驗」。

> **這個查證結果反過來強化了 §11.4 的設計**：既然沒有任何一家保證 Python 可用、也沒有一家正式承諾標準庫完整，那「**沒有一支 script 在必要路徑上**」就不是保守，而是唯一正確的架構。

### 11.2 素材格式：為什麼是 JSON 不是 YAML

parser 的有無只影響一格。**agent 本身讀 YAML 和 JSON 一樣好，那從來不是考量點**：

| 環境 | 需要 parser 嗎 |
|---|---|
| 有程式執行 + 有 PyYAML | 不需要，直接 `yaml.safe_load` |
| 有程式執行 + 無 PyYAML | ← **只有這格** JSON 才佔便宜 |
| 無程式執行 | 不需要 parser，agent 自己讀 |

素材檔是 **agent 產出的**，不是人手寫的，所以「YAML 可以寫註解」這個常見理由在這裡**不成立**——沒有人要寫註解。合法列舉值改寫在 `references/sections/09_materials.md`，比放在資料檔的註解裡更合適（agent 讀規格，不讀資料）。

實際取捨：

| | 受限 YAML | JSON |
|---|---|---|
| 依賴 | 需要 PyYAML 或自帶 reader | **零依賴**（`json` 是標準庫） |
| 出錯時的行為 | **可能靜默誤判**：PyYAML 走 YAML 1.1，`open_hours: 12:30` 未加引號會解析成整數 `750`（六十進位）；`no` / `off` 變成布林 `False` | 直接解析失敗，不會安靜地給錯值 |
| git diff | 新增一筆 = 純新增 | 陣列尾端不能有逗號，**新增一筆會動到前一筆** |
| 手動編輯 | 舒服 | 難受 |

**定案 JSON**：素材由機器產出、幾乎不手改，「靜默誤判」的風險遠大於「diff 多一行」的損失。diff 的損失靠 §7.2 的輸出約定（欄位順序固定、來源物件單行、只動該筆）補回大半，且 `render_materials` 產生的 md 才是給人看的版本。

連帶結果：**不需要 `yaml_lite.py`**，整個 skill 內不再有任何 YAML 檔。

### 11.3 三支 script 與各自的 md 後備

| script | 做什麼 | 為什麼值得寫成程式 | 無 Python 時的後備 |
|---|---|---|---|
| `validate_materials.py` | 執行 §7.3 六條硬約束，輸出違規清單 | 全是機械規則（計數、比對日期、檢查參照完整性）。agent 逐條自查既慢又易漏 | `checklists/validate_materials.md`：編號步驟 + 明確計數指令，agent 手動跑一遍 |
| `render_materials.py` | JSON → md 表格，並強制 §7.2 輸出約定 | 避免手抄抄錯價位、漏店家；順便鎖住欄位順序讓 diff 乾淨 | agent 照 JSON 逐筆抄寫，寫完後自行核對筆數 |
| `scrub_check.py` | 從 trip_profile 抽 token，掃描待版控檔案是否外洩 | 字串比對，程式做零失誤 | `checklists/scrub_check.md`：列出必查的 8 類 token，逐檔搜尋 |

### 11.4 三條鐵則

1. **沒有一支 script 是必要路徑**。skill 在任何環境都要能完整跑完，script 只決定快慢與嚴謹度。
2. **script 失敗不得中斷流程**——退回 md checklist 並在 progress.md 記錄「本次以 checklist 校驗」。
3. **script 不做檢索、不做判斷**，只做校驗與格式轉換。所有需要判斷的事留給 agent，這樣無程式執行的環境才可能等價降級。

---

## 12. 建議補進架構的資訊

### 必補（第一版就要有）

1. **緊急應變 / 網路漫遊 / 免稅退稅**——如 §1.3，舊版有、新規劃漏了，其中緊急應變風險最高。
2. **訂位與預約清單**：哪些景點、餐廳、體驗**必須事先訂**，含開放訂位時間、訂位平台、是否需要當地電話號碼。這是最容易讓整套行程崩掉的一項，而現有與新規劃**都沒有**。實測樣本裡的「南怡島包車」「汝矣島夜遊漢江」正是這類必須先訂的項目。放在 `plan/01_flight_stay.md` 一節，並在 `pre_trip_checklist.md` 時間軸上標點。
3. **來源時效與可信度分級**：每個 source 帶 `published` 日期與 `tier`（official / platform / blogger）。目前規範只要求深層連結、沒有日期欄位，導致「強調近一年最新資訊」這條約束**無法被檢查**。加上 `published` 後，校驗才能機械執行。

### 強烈建議

4. **預算與花費估算**：機票住宿為已知值，餐飲/交通/門票/購物做每日概估，並反映各支付方式的手續費與匯損。整套架構目前完全沒有金錢維度——而實測樣本第一行就是「換匯 TWD$2000」，可見使用者本來就在想這件事。
5. **天氣與季節實況**：氣候常態值 + **日出日落時間**（直接影響半日行程怎麼排，例如首爾十月中約 17:50 天黑，觀景台就該提前）+ 當季限定活動（楓葉/慶典）。
6. **每半天的 Plan B**：已寫進 §8 規則 6，素材庫用 `rainy_day_ok` 支援。
7. **回程/離境清單**：退稅、交通卡退卡餘額、機場報到時間回推、行李超重應對、免稅品攜帶規範。這是行前 checklist 的鏡像，同樣容易漏。

### 可延後（第二版）

8. **語言小抄**：點餐/問路/求助常用句 + 當地語言關鍵字（讓地圖 App 搜得到店家）。
9. **無障礙路線**：地鐵站電梯出口編號層級的資訊，延伸自友善度評分。
10. **成品時效標記與重跑指引**：每份成品 md 檔頭帶 `last_verified`，README 標明「出發前 7 天必須重跑的章節」（通關、交通末班車、店家營業狀態）。

---

## 13. 分階段實作計畫

每個 Phase 結束都應該是**可獨立驗收**的狀態。

### Phase 0：封存與清場
- `git mv` 現有檔案進 `archive/`，寫 `archive/README.md` 封存 banner。
- 根目錄只剩 `README.md`（暫改「改造中」）、`skill_update_plan.md`、`archive/`、`.gitignore`。
- **驗收**：`git log` 可追溯每個舊檔去向；根目錄乾淨。

### Phase 1：骨架、可攜性、隱私分層
- 建 `skills/travel-plan/` 目錄樹。
- 寫 `SKILL.md`（frontmatter、環境自檢、啟動對話、階段機、路由表）。
- 寫 `references/portability.md`、`references/privacy.md`、`references/progress_protocol.md`。
- 寫 `templates/trip_profile.template.md`、`trip_context.template.md`、`progress.template.md`。
- 建 `.gitignore`。
- **驗收**：(a) Claude Code 觸發能建 trip 資料夾、請使用者填表、目的地留空正確中止；(b) **把 skill 打包 zip 上傳 claude.ai 網頁版，同樣能走到「請填 trip_profile」這一步**，且不會問平行模式。

### Phase 2：檢索規範與通用知識骨架
- 寫 `references/research_rules.md`（承襲舊引用/查證規範 + 新增 tier 與 published）。
- 寫 `templates/knowledge/` 六份**骨架**（結構 + 必答問題 + `{{查最新}}` 佔位；**不得寫死任何數字、金額、期限或網址**）。參考 `archive/travel_general_mindset.md` 的分類邏輯，但不搬事實。
- 寫骨架填充與快取規格（§6.1）。
- **驗收**：(a) 給定 trip_context，agent 填出 `plan/00_general.md`，每個易變事實都有深層來源與 `last_verified`；(b) **骨架本身通過「零事實」檢查**——grep 不到具體數字、金額與網址；(c) 換一個非台灣出發的 trip_context，產出內容跟著換（不會冒出健保署或桃園機場）。

### Phase 3：Wave 1 主題規格（**用真實樣本實測**）
- 寫 `references/sections/01~08, 11`（9 份）+ `references/workflow.md`。
- **實測輸入**：使用者本機的真實行程草稿（放在 `trips/{trip}/private/input/`，不進版控）。
- **驗收**：
  - 序列模式跑完 Wave 1，9 份 md 產出，所有連結通過抓取驗證；
  - progress.md 逐步更新且每步有 commit；
  - **`trip_context.json` 不含訂房確認號、訂房人姓名、航班號、飯店全名與門牌**，`scrub_check` 通過；
  - `private/` 未被 git 追蹤。

### Phase 4：素材庫與 scripts
- 寫 `templates/spots.schema.json`、`food.schema.json`、`references/sections/09_materials.md`（含列舉值與 §7.2 輸出約定）。
- 寫 `scripts/validate_materials.py`、`render_materials.py`、`scrub_check.py`（全部 stdlib）。
- 寫 `references/checklists/` 兩份 md 後備。
- **驗收**：(a) JSON 通過七條校驗（每區觀光客 3 + 當地人 3、來源日期、rainy_day_ok、參照完整性、列舉值合法）；(b) **script 不 import 任何第三方套件**（靜態檢查 import 清單）；(c) 停用 script 改走 md checklist，得到相同的違規判定。

### Phase 5：行程安排
- 寫 `references/sections/10_itinerary.md`。
- **驗收**：同一份素材庫產出 3 套明顯不同、各自內部距離合理的行程；**抵達日（清晨落地、15:00 才能入住）與回程日（下午起飛）的可用時數計算正確**；每半天都有 Plan B；草稿指名的景點全數涵蓋。

### Phase 6：平行模式與收尾
- 在具備子 agent 派發能力的宿主實測平行模式（Wave 1 分派子 agent），驗證主 agent 收斂與跨章節呼應檢查。
- 改寫 `README.md`：三種環境的安裝方式、模式取捨、產出說明、隱私說明、與 travel 部落格的銜接點。
- **驗收**：同一份 trip_profile 分別用平行與序列跑，產出結構一致；README 能讓沒讀過本計畫的人在**網頁版**自己跑起來。

---

## 14. 風險與取捨

| 風險 | 對策 |
|---|---|
| SKILL.md 膨脹，每次觸發付全額 token | 主檔只放流程與路由，主題規格放 references 按需讀取 |
| 網頁版上傳後找不到 skill 外的檔案 | skill 資料夾自我完備，通用知識骨架放 templates 內 |
| 網頁版跨對話遺失進度 | progress.md 設計成自足的接手包，明列「接續包」檔案清單 |
| 平行模式子 agent 無法問使用者 | 門檻檢查與模式選擇一律在派工前完成；子 agent 遇到必須決策的事一律標 `[待確認]` 回報 |
| agent 無法清空自己 context | 序列模式明確要求使用者操作，skill 負責產生足夠的交接事項 |
| 通關/保險/緊急的幻覺風險 | 三塊設最嚴格等級：只採官方第一手來源，每條後綴連結，無法驗證一律 `[待確認]` |
| agent 產出的 JSON 格式壞掉 | JSON 解析失敗即報錯（不會靜默誤判）+ `validate_materials` 守門，schema 檔同時當範例 |
| 「近一年最新資訊」無法驗證 | 強制 `published` 欄位，交給校驗檢查 |
| **個資進版控** | `private/` gitignore + trip_context 抽象化 + commit 前 scrub 檢查 + 首次 commit 前人工確認 |
| script 在某些環境跑不起來（含本機 CLI 沒裝 Python、網頁版未啟用 code execution） | 啟動時實測 `python3 --version`；三條鐵則（§11.4）：不是必要路徑、失敗不中斷、只做校驗與轉換 |
| 散佈出去的知識變舊、或只適用單一出發國 | 只散佈骨架不散佈事實（§6.1），事實一律現查並附 `last_verified` |
| 兩個 repo 同步漂移 | 本階段刻意不自動化銜接 |

---

## 15. 與 travel 部落格的銜接點（本階段不實作）

- `travel_guide` 產出的成品 md 是**內容真實來源**，純 md，不含部落格專屬語法。
- 未來要進 `travel` 部落格需要的轉換：加上 front matter、把表格與提示區塊改寫成該專案的 card DSL（見 `travel/doc/card_dsl.md`）、依 `travel/doc/doc_style.md` 調整標題階層。
- 選哪幾份搬過去由使用者當下決定，**不做全量同步**——素材庫、progress.md、待確認清單、`private/` 都不適合公開。

---

## 16. 待你確認的事項

1. ~~素材格式~~ **已定案：JSON**（§11.2）。
2. ~~`plan/` 要不要進版控~~ **已定案：進版控**。去識別化後的 `trip_context.json`、`progress.md`、`materials/*.json`、`plan/*.md` 全部納入 git；只有 `trips/*/private/` 排除。
3. ~~通用知識種子~~ **已定案：改為骨架模板，不散佈事實**（§6.1）。
4. ~~Python 標準庫是否為安全假設~~ **已查證完畢**（§2.6、§11.1）：Python 標準庫是三家的最大公約數，但「一定有 Python」不成立，需在啟動時實測 `python3 --version`。
