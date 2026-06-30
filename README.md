# ✈️ AI 旅遊規劃系統 (Travel Guide System)

本專案是一個模組化、自動化的旅遊規劃工具。藉由將**「固定心法」**與**「動態更新」**解耦，並使用本地設定檔保護隱私，您可以讓 AI Agent 協助您爬取最新旅遊資訊，生成量身打造、且能「無腦照著跑」的旅遊規劃書。

---

## 📂 專案目錄結構與說明

- ⚙️ **[travel_config.yml](file:///home/lawrencechh/j/travel_guide/travel_config.yml)**:
  本地設定檔（YAML 格式）。包含您的出發地、目的地、起訖機場、航空公司、旅遊日期、電信商、同伴資訊以及備註偏好。
  *(此檔案已自動加入 [.gitignore](file:///home/lawrencechh/j/travel_guide/.gitignore)，確保您的行程隱私不被推上 Repository。)*

- 📝 **[travel_template.md](file:///home/lawrencechh/j/travel_guide/travel_template.md)**:
  動態欄位模板。僅包含需要 Agent 動態爬取並更新的區塊（如：保險、網路、入境快速通關、機場接駁、免稅、當地習俗與客製化行程）。

- 🧳 **[travel_general_mindset.md](file:///home/lawrencechh/j/travel_guide/travel_general_mindset.md)**:
  固定心法文件。包含打包原則、保險索賠黃金清單、通用機場登機流程與同伴照護守則。這部分內容為通用且固定的旅遊知識，不需要 Agent 重複爬取，您可以在規劃書生成後手動複製合併。

- 🎯 **[prompt_generate_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_generate_trip.md)**:
  首次生成專屬規劃書的 Agent Prompt 指令。要求 Agent 讀取設定檔與模板，並爬取最新官方行李、支付、保險與接駁資訊，生成 `travel_{目的地}.md`。內含「不確定與未知資訊之註記規範」。

- 🔄 **[prompt_update_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_update_trip.md)**:
  增量維護已生成規劃書的 Agent Prompt 指令。在您出發前，讓 Agent 讀取已有的 `travel_{目的地}.md`，重新檢查連結效力、電信與交通時刻表是否有變更，僅修改受影響之文字。

---

## 🚀 如何使用這套系統

### 步驟 1：配置您的本地設定檔
開啟 [travel_config.yml](file:///home/lawrencechh/j/travel_guide/travel_config.yml)，填入您這次旅行的基礎資訊。
如果有哪些特定要求（如：需要投保海外突發疾病險、希望多安排美食行程、避免長樓梯景點等），請使用 YAML 的多行語法 `notes: |` 以自然語言自由編寫在備註中。

### 步驟 2：執行 Agent
#### 情境 A：第一次前往該目的地
將 [prompt_generate_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_generate_trip.md) 的內容作為 Prompt 指令提供給您的 AI Agent，它將會生成專屬於您的動態旅遊書 `travel_{目的地}.md`。

#### 情境 B：出發前一週進行資訊更新
將 [prompt_update_trip.md](file:///home/lawrencechh/j/travel_guide/prompt_update_trip.md) 提供給 AI Agent，它將只針對已經生成的 `travel_{目的地}.md` 內部的動態標籤進行最新資費、時刻表與退稅門檻的局部更新與修正。

### 步驟 3：手動貼上固定心法
規劃書生成後，您可以直接將 [travel_general_mindset.md](file:///home/lawrencechh/j/travel_guide/travel_general_mindset.md) 內您有需要的固定心法（如行李打包清單、索賠黃金清單）複製並合併到產出的規畫書中，即完成您最完美的旅遊指南！
