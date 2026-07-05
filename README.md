# ✈️ AI 旅遊規劃系統 (Travel Guide System)

本專案是一個模組化、自動化的旅遊規劃工具。藉由將**「固定心法」**與**「動態更新」**解耦，並使用本地設定檔保護隱私，您可以讓 AI Agent 協助您爬取最新旅遊資訊，並依據「四大時間線篇章」生成量身打造、且能「無腦照著跑」的旅遊規劃書。

## 🧭 兩種執行模式：經濟版 vs 深度版

| | 經濟版（根目錄 prompt） | 深度版（`orchestrator/`） |
|---|---|---|
| 執行方式 | 單一 Agent 對話內完成全部章節 | 主管 Agent 派工給多個**真實子 agent**（章節研究員）並行深挖，再收斂組裝 |
| 適用環境 | 任何具備 WebSearch/WebFetch 的 Claude 對話 | 需要**能派發子 agent 的框架**（如 Claude Code、antigravity 等 orchestrator 模式） |
| Token 成本 | 較省 | 較高（多 agent 並行），換取每章節更深入的檢索與驗證 |
| 何時選用 | 一般規劃、快速產出、修改設定後想省 token 重跑 | 想要對每個章節做更深入、更多來源交叉比對的規劃（如首次生成一份重要行程） |

兩種模式共用同一份 `travel_config.yml` 設定檔與 `travel_template.md` 資訊架構藍圖，產出檔案格式完全相同，可互相替換使用、不影響既有規劃書。

---

## 📂 專案目錄結構與說明

- ⚙️ **[travel_config.yml](file:///home/lawrencechh/j/travel_guide/travel_config.yml)**:
  本地設定檔（YAML 格式）。核心欄位是兩段自由文字：`trip_route`（一段話涵蓋出發地、出發/抵達機場含航廈、目的地、去回程航空公司；**必填**，Agent 會自動解析出各項細節，缺目的地時會停下來請您補上）與 `companions`（一段話描述同伴人數/年齡/關係；選填，留空則以一般成人旅客為假設）。此外包含旅遊日期、選填的檢索限定年份 (`target_year`)、電信商、**寫作風格偏好 (`tone_style`)**、**美食偏好 (`preferences.food_preferences`)** 以及備註偏好。
  *(此檔案已自動加入 [.gitignore](file:///home/lawrencechh/j/travel_guide/travel_config.yml)，確保您的行程隱私不被推上 Repository。)*
  **設計原則：填越少，Agent 自動補的越通用；填越細，規劃越客製化。**（目的地是唯一例外——它無法被自動猜測，留空會被要求補上。）

- ⚙️ **[travel_config_template.yml](file:///home/lawrencechh/j/travel_guide/travel_config_template.yml)**:
  設定檔範本。提供給使用者複製並修改為 `travel_config.yml` 使用，內含 `trip_route`／`companions` 的填寫範例、風格偏好設定（`tone_style`）、美食偏好（`preferences.food_preferences`，留空範例）與 `notes` 自訂需求範例。

- 📝 **[travel_template.md](file:///home/lawrencechh/j/travel_guide/travel_template.md)**:
  **資訊架構藍圖**（非動態欄位模板，不含任何 `<!-- DYNAMIC_* -->` 標籤或 `{變數}` 佔位符）。純粹定義行前、機場、在地、緊急四大部分共 11 個章節的順序與每章產出重點，經濟版與深度版 prompt 皆以此為共同編排依據。

- 🧳 **[travel_general_mindset.md](file:///home/lawrencechh/j/travel_guide/travel_general_mindset.md)**:
  固定心法文件。包含打包原則、保險索賠黃金清單、通用機場登機流程與同伴照護守則。這部分內容為通用且固定的旅遊知識，不需要 Agent 重複爬取，您可以在規劃書生成後手動複製合併。

- 🎯 **[prompt_generate_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_generate_trip.md)**（經濟版・首次生成）:
  首次生成專屬規劃書的 Agent Prompt 指令。
  *(內含 **「🤖 多代理人內部協作工作流」**。查證數據後先輸出無 dynamic 標籤的乾淨原始規劃書 `travel_{目的地}.md`；接著指派 **【資深編輯】** 依據設定檔風格潤色全文語氣，輸出最終精修版 **`travel_{目的地}_edited.md`**。引用規範要求「深層連結 + 標題」，並由【資訊查證員】以 WebFetch 實際開啟每個連結驗證。)*

- 🔄 **[prompt_update_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_update_trip.md)**（經濟版・增量更新）:
  增量維護已生成規劃書的 Agent Prompt 指令。
  *(增量更新後，同樣會自動啟動 **【資深編輯】** 重新潤色，並同步更新覆寫精修版 **`travel_{目的地}_edited.md`**。連結驗證與美食推薦規則與首次生成版一致。)*

- 🧑‍🤝‍🧑 **[orchestrator/](file:///home/lawrencechh/j/travel_guide/orchestrator/)**（深度版）:
  - `prompt_orchestrator.md`：主管 prompt，讀取設定檔與藍圖後，依四部分把任務拆成章節包，並行派給章節研究員子 agent，收斂組裝、總查證、再交由資深編輯潤色。
  - `prompt_section_worker.md`：章節研究員 prompt，只負責深挖被指派的章節，遵守與經濟版相同的引用規範，行程章節額外遵守五大公式 A–F 與美食多元約束。
  - 需要可派發真實子 agent 的框架；不具備此能力的環境請改用根目錄經濟版 prompt。

---

## 🚀 如何使用這套系統

### 步驟 1：配置您的本地設定檔
1. 開啟 [travel_config.yml](file:///home/lawrencechh/j/travel_guide/travel_config.yml)，用一段自然語言填寫 `trip_route`（**必填**：至少要看得出目的地，出發/抵達機場航廈與航空公司可省略，Agent 會自動查合理預設）。
2. `companions`（選填）：一段話描述人數、年齡、關係即可，不用分開填欄位。留空則 Agent 以一般成人旅客為假設。
3. `target_year`（選填）：留空會自動推導自旅遊日期涵蓋的年份；若想額外指定查詢年份（如跨年行程、想順便查隔年新制）才需要填。
4. 填入希望的 **文章寫作風格偏好 (`tone_style`)**。
5. `preferences.food_preferences`（選填）：用一段自由文字寫下辣度、想吃品類、忌口即可。**留空**的話，Agent 會自動啟動「多元美食自主蒐集」，橫跨正餐名店/在地小吃/咖啡廳甜點/伴手禮特產等類別，適合不熟該國飲食的旅客。
6. 任何其他特定偏好（例如：希望優先找台灣部落客食記、避開長樓梯、指名必去景點），請統一使用 YAML 的多行語法 `notes: |` 以自然語言直接編寫在備註中即可。

### 步驟 2：選擇模式並執行 Agent
先參考上方「兩種執行模式」表格決定要用**經濟版**還是**深度版**。

#### 經濟版・情境 A：第一次針對草稿進行完整補全與驗證
將 [prompt_generate_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_generate_trip.md) 的內容作為 Prompt 指令提供給您的 AI Agent。執行完成後，您會獲得兩個檔案：
1. **`travel_{目的地}.md`**：無 dynamic 標籤的乾淨原始規劃書（用於日後更新）。
2. **`travel_{目的地}_edited.md`**：精修寫作風格後的最終旅遊書（用於直接閱讀）。

#### 經濟版・情境 B：出發前一週進行資訊更新
將 [prompt_update_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_update_trip.md) 提供給 AI Agent，它將針對 `travel_{目的地}.md` 進行局部修正，並自動重新生成風格修飾版 `travel_{目的地}_edited.md`。

#### 深度版：需要更深入檢索時
在具備派發子 agent 能力的框架（如 Claude Code）中，將 [orchestrator/prompt_orchestrator.md](file:///home/lawrencechh/j/travel_guide/orchestrator/prompt_orchestrator.md) 作為主管 Agent 的指令啟動，它會自動依 [orchestrator/prompt_section_worker.md](file:///home/lawrencechh/j/travel_guide/orchestrator/prompt_section_worker.md) 並行派工給章節研究員子 agent，最終同樣產出 `travel_{目的地}.md` 與 `travel_{目的地}_edited.md` 兩個檔案。

### 步驟 3：手動貼上固定心法
規劃書生成後，您可以直接將 [travel_general_mindset.md](file:///home/lawrencechh/j/travel_guide/travel_general_mindset.md) 內您有需要的固定心法（如行李打包清單、索賠黃金清單）複製並合併到產出的規畫書中，即完成您最完美的旅遊指南！
