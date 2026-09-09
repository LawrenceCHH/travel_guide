---
name: travel-plan
description: 協助使用者規劃出國自助旅行的完整行前準備與行程安排。觸發情境包含：旅遊規劃、旅行規劃、行程安排、行程規劃、出國準備、自助旅行、自由行、trip planning、travel plan、itinerary、travel itinerary、trip itinerary、plan a trip、旅遊行程、機票住宿整理、簽證通關準備、旅遊保險比較、國外網路方案、當地交通與支付、免稅退稅、當地習慣禁忌、緊急應變準備、行前打包清單、多天行程規劃、家庭/親子/長輩旅遊規劃。當使用者提到要去某個國家/城市旅遊、要排幾天幾夜的行程、要準備出國相關事項（簽證、保險、網路、交通、退稅、打包）、或提供了機票/訂房草稿要整理成完整行程時，載入本 skill。
---

# travel-plan

引導使用者從任意輸入（既有草稿、片段資訊、或完全空白）產出一趟旅程的完整行前準備與 3 套行程安排。**任何環境都必須能完整跑完**——skill 啟動時先自檢環境能力，依能力優雅降級，不因缺少 git、子 agent 或程式執行而中斷。

> 本檔只放流程與路由，主題規格一律按需讀取 `references/`，不在此重複內容。**本 skill 資料夾自我完備**，執行時不需要、也不得依賴資料夾外的任何檔案。

## 0. 核心原則（貫穿全流程）

- **所有 script 都是可選加速器**：`scripts/*.py` 失敗、不存在、或環境無法執行時，一律退回 `references/checklists/` 的等效手動流程，並在 `progress.md` 記錄「本次以 checklist 校驗」。**不得因 script 失敗而中斷任務。**
- **原始個資不進版控**：使用者提供的原始輸入（含姓名、訂位代號、航班號、飯店全名門牌）留在 `trips/{trip}/private/`；只有去識別化後的 `trip_context.json` 及其下游成品才進版控或分享。細則見 `references/privacy.md`。
- **留空即預設**：使用者填越少，agent 補越通用，缺欄位不中斷流程；所有推斷值標記待覆核。
- **`[待確認：原因]`**：查不到就標記，嚴禁編造。
- **引用規範**：深層連結（去掉 domain 後路徑不可為空）＋`[文章標題 - 作者/站名](網址)`＋禁止自行拼湊路徑＋必須是搜尋/抓取實際回傳的網址；逐一開連結驗證「回傳成功、內容相符、是深層文章頁」，不通過就標 `[待確認：連結無法驗證]`。詳見 `references/research_rules.md`。

## 1. 啟動順序（順序不可調換）

1. **環境能力自檢**，寫入 `progress.md`「環境」欄：
   - 網頁搜尋／抓取？檔案讀寫？子 agent 派發？git？
   - 程式執行：**實測執行 `python3 --version`（失敗再試 `python --version`）**，不得從宿主類型推斷。
   - **無網頁搜尋 → 這是唯一硬需求，明確告知使用者無法執行並中止。**
   - 各項能力的判定方式與降級路徑見 `references/portability.md`。
2. **取得使用者資訊**（依優先序）：讀既有檔案 ▸ 引導式提問（一次問一批 3~5 題，附「不回答會怎樣」）▸ 全部走預設。細節、必抽欄位表與抽不到時的行為見 `references/intake.md`。
3. **目的地門檻檢查**：若抽不到目的地（既非既有資料、也非使用者回覆），輸出以下固定句並**中止流程**，不得續問其他事項：

   > 「我需要先知道您的旅遊目的地才能開始規劃，請告訴我您想去哪裡（國家或城市）。」

4. **產出 `trip_context.json`**，請使用者確認去識別化結果（人工關卡，不可跳過）。格式與去識別化規則見 `references/privacy.md`。
5. **只有具備子 agent 派發能力時才問**：要平行還是序列？（見 §3）**此步必須在派任何工之前完成**——派工後即為非互動式，子 agent 沒機會再問使用者，所有需要使用者決定的事必須在此之前一次問完。無子 agent 能力時不問這一題，直接走序列。
6. **建立 `progress.md`**，開始執行。格式見 `references/progress_protocol.md`。

## 2. 三種模式與 Wave 依賴（摘要，細節見 `references/workflow.md`）

| 模式 | 適用 | 摘要 |
|---|---|---|
| 序列 | 無子 agent 能力時的唯一選項 | 單一 agent 逐主題執行，定期清空 context，靠 `progress.md` 接手 |
| 平行 | 具子 agent 派發能力時 | 主 agent 分波派工，Wave 內主題同時深挖 |
| 混合（預設推薦） | 具子 agent 能力時 | 檢索類主題平行，素材庫與行程安排序列，依賴結構決定 |

Wave 依賴（詳見 `references/workflow.md` §依賴分析）：

```
前置：00 通用知識裁剪 ｜ 01 行程資訊整理（主 agent 自己做）
Wave 1（可完全平行）：02 03 04 05 06 07 08 11
Wave 2（依賴 05＋01 的住宿區位）：09 素材庫
Wave 3（依賴 09＋05＋首尾時刻）：10 行程安排（3 方案）
```

跨主題呼應檢查（推薦 App 是否呼應交通/支付、行程接駁是否與交通章節一致、素材庫店家是否被行程實際用到）由主 agent 在收斂時執行，方法見 `references/workflow.md`。

## 3. 階段機與路由表

**主檔不重複任何主題的檢索規則或產出規格，只給路徑。** 序列模式每階段只讀自己那份 + 共用規則；平行模式每個子 agent 只帶自己那份 + `references/research_rules.md`。

| 階段 | 主題 | 讀哪份 reference | 產出 |
|---|---|---|---|
| 前置 | 通用知識裁剪 | `templates/knowledge/*.template.md`（六份骨架）+ `references/research_rules.md` | `plan/00_general.md` |
| 01 | 行程資訊整理 | `references/sections/01_flight_stay.md` | `plan/01_flight_stay.md` |
| 02 | 機場通關 | `references/sections/02_immigration.md` | `plan/02_immigration.md` |
| 03 | 保險 | `references/sections/03_insurance.md` | `plan/03_insurance.md` |
| 04 | 網路與漫遊 | `references/sections/04_connectivity.md` | `plan/04_connectivity.md` |
| 05 | 交通資訊 | `references/sections/05_transport.md` | `plan/05_transport.md` |
| 06 | 支付方式 | `references/sections/06_payment.md` | `plan/06_payment.md` |
| 07 | 免稅與退稅 | `references/sections/07_tax_refund.md` | `plan/07_tax_refund.md` |
| 08 | 當地習慣 | `references/sections/08_local_customs.md` | `plan/08_local_customs.md` |
| 09 | 素材庫 | `references/sections/09_materials.md` + `templates/spots.schema.json` / `food.schema.json` | `materials/spots.json` / `materials/food.json` |
| 10 | 行程安排（3 方案） | `references/sections/10_itinerary.md` | `plan/10_itinerary.md` |
| 11 | 緊急應變 | `references/sections/11_emergency.md` | `plan/11_emergency.md` |

其餘共用檔：

| 用途 | 路徑 |
|---|---|
| 檢索/引用/查證規範 | `references/research_rules.md` |
| 環境自檢與降級路徑 | `references/portability.md` |
| 隱私分層與去識別化規則 | `references/privacy.md` |
| `progress.md` 格式與接手協議 | `references/progress_protocol.md` |
| 三模式與 Wave 調度細節 | `references/workflow.md` |
| script 的手動後備 | `references/checklists/validate_materials.md`、`references/checklists/scrub_check.md` |
| 使用者資訊取得與必抽欄位 | `references/intake.md` |
| 選填輔助問卷 | `templates/trip_profile.template.md` |
| 去識別化脈絡檔 schema | `templates/trip_context.schema.json` |
| `progress.md` 空白模板 | `templates/progress.template.md` |
| 成品共用檔頭 | `templates/section.template.md` |

## 4. 主題總覽（11 主題，風險分級）

01 行程資訊｜02 機場通關｜03 保險｜04 網路與漫遊｜05 交通資訊｜06 支付方式｜07 免稅與退稅｜08 當地習慣｜09 素材庫｜10 行程安排｜11 緊急應變。

**02 通關、03 保險、11 緊急應變為最嚴格等級**：只採官方第一手來源，每條資訊後綴來源連結，不接受概括引用，無法驗證一律 `[待確認]`。

## 5. 序列模式的記憶體管理（agent 不能清空自己的 context）

每個主題完成後：讀 `progress.md` → 執行 1 個主題 → 寫成品 md → 更新 `progress.md` → 有 git 就 commit（commit 前必跑 scrub 檢查）／沒 git 就更新變更紀錄區塊 → **明確告訴使用者**下一步該做什麼（有持久檔案系統：`/clear` 後回覆「繼續」；網頁版：下載接續包上傳到新對話後回覆「繼續」）。完整協議見 `references/progress_protocol.md`。

## 6. 產出結構

```
trips/{trip}/
├── private/            # .gitignore，永不進版控（原始輸入、個人化成品）
├── trip_context.json   # 去識別化，進版控
├── progress.md          # 進版控
├── materials/           # spots.json / food.json，進版控
└── plan/                 # 00~11 主題成品，進版控
```
