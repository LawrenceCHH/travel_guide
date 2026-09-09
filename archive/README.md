# 封存區（archive/）

> **本目錄僅供引用，不描述現況。**

這裡是 `travel_guide` 改造為 `skills/travel-plan/` Agent Skill 之前的舊資產，整批搬移進來以保留 git 歷史（`git mv`），純粹供撰寫新 skill 內容時查閱、借用分類邏輯或心法角度。

**不要根據本目錄內容推斷目前架構、現有流程或目前有效的規範。** 目前有效的規格一律以 `skill_update_plan.md` 與 `skills/travel-plan/` 底下的檔案為準。

## 目錄內容

- `prompt_generate_trip.md` / `prompt_update_trip.md` / `orchestrator/`：舊的雙軌 prompt 與 orchestrator 派工機制。
- `travel_template.md` / `travel_config_template.yml` / `travel_general_mindset.md`：舊的成品模板、設定檔模板、通用心法（**內容為台灣出發專屬且部分事實已過期，只能借用分類邏輯，不能搬事實**，見 `skill_update_plan.md` §6.1）。
- `travel_韓國首爾*.md` / `Korean/` / `index.html` / `plan.md` / `verification_report.md` / `web_design_preference.md` / `travel_config.yml`：舊的首爾行程實測產出與週邊素材。
- `docs/`：舊的需求文件。
- `design_skills_claude/`、`design_skills_agents/`：與旅遊規劃無關的設計類 skill（原 `.claude/skills/`、`.agents/skills/`），與本次改造無關，一併封存以保留 git 歷史。

## 已知限制

- 部分連結、事實、金額、期限等資訊已過期，不代表目前有效狀態。
- `Korean/` 目錄下含使用者原始輸入與個資性質內容，僅供內部參考，**不應被搬進任何新產出**。
