# ✈️ AI 旅遊規劃系統 (Travel Guide System)

本專案是一個模組化、自動化的旅遊規劃工具。藉由將**「固定心法」**與**「動態更新」**解耦，並使用本地設定檔保護隱私，您可以讓 AI Agent 協助您爬取最新旅遊資訊，並依據「四大時間線篇章」生成量身打造、且能「無腦照著跑」的旅遊規劃書。

---

## 📂 專案目錄結構與說明

- ⚙️ **[travel_config.yml](file:///home/lawrencechh/j/travel_guide/travel_config.yml)**:
  本地設定檔（YAML 格式）。包含您的出發地、目的地、起訖機場、航空公司、旅遊日期、電信商、同伴資訊、**寫作風格偏好 (`tone_style`)** 以及備註偏好。
  *(此檔案已自動加入 [.gitignore](file:///home/lawrencechh/j/travel_guide/travel_config.yml)，確保您的行程隱私不被推上 Repository。)*

- ⚙️ **[travel_config_template.yml](file:///home/lawrencechh/j/travel_guide/travel_config_template.yml)**:
  設定檔範本。提供給使用者複製並修改為 `travel_config.yml` 使用，內含豐富的參數說明、風格偏好設定（`tone_style`）與 `notes` 自訂需求範例。

- 📝 **[travel_template.md](file:///home/lawrencechh/j/travel_guide/travel_template.md)**:
  動態欄位模板。包含行前、機場、在地、緊急四大部分，共 11 個需要 Agent 動態爬取並更新的區塊。

- 🧳 **[travel_general_mindset.md](file:///home/lawrencechh/j/travel_guide/travel_general_mindset.md)**:
  固定心法文件。包含打包原則、保險索賠黃金清單、通用機場登機流程與同伴照護守則。這部分內容為通用且固定的旅遊知識，不需要 Agent 重複爬取，您可以在規劃書生成後手動複製合併。

- 🎯 **[prompt_generate_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_generate_trip.md)**:
  首次生成專屬規劃書的 Agent Prompt 指令。
  *(內含 **「🤖 多代理人內部協作工作流」**。在查證數據後，先輸出帶有 DYNAMIC 標籤的原始規劃書 `travel_{目的地}.md`；接著指派 **【資深編輯】** 依據設定檔風格潤色全文語氣，輸出最終無標籤、給旅客直接閱讀的精修版 **`travel_{目的地}_edited.md`**。)*

- 🔄 **[prompt_update_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_update_trip.md)**:
  增量維護已生成規劃書的 Agent Prompt 指令。
  *(增量更新後，同樣會自動啟動 **【資深編輯】** 重新潤色，並同步更新覆寫精修版 **`travel_{目的地}_edited.md`**。)*

---

## 🚀 如何使用這套系統

### 步驟 1：配置您的本地設定檔
1. 開啟 [travel_config.yml](file:///home/lawrencechh/j/travel_guide/travel_config.yml)，填入您這次旅行的基礎資訊、同伴年齡、以及希望的 **文章寫作風格偏好 (`tone_style`)**。
2. 任何特定偏好（例如：希望優先找台灣部落客食記、避開長樓梯、指名必去景點），請統一使用 YAML 的多行語法 `notes: |` 以自然語言直接編寫在備註中即可。

### 步驟 2：執行 Agent
#### 情境 A：第一次針對草稿進行完整補全與驗證
將 [prompt_generate_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_generate_trip.md) 的內容作為 Prompt 指令提供給您的 AI Agent。執行完成後，您會獲得兩個檔案：
1. **`travel_{目的地}.md`**：保留動態標籤的原始規劃書（用於日後更新）。
2. **`travel_{目的地}_edited.md`**：精修寫作風格後的最終旅遊書（用於直接閱讀）。

#### 情境 B：出發前一週進行資訊更新
將 [prompt_update_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_update_trip.md) 提供給 AI Agent，它將針對 `travel_{目的地}.md` 進行局部修正，並自動重新生成風格修飾版 `travel_{目的地}_edited.md`。

### 步驟 3：手動貼上固定心法
規劃書生成後，您可以直接將 [travel_general_mindset.md](file:///home/lawrencechh/j/travel_guide/travel_general_mindset.md) 內您有需要的固定心法（如行李打包清單、索賠黃金清單）複製並合併到產出的規畫書中，即完成您最完美的旅遊指南！
