# 驗收測試第一輪（固定矩陣，三格）

> 目的：驗證本輪已修改的 4 項規格是否真的生效、可執行，並用兩個全新情境（換目的地、模擬能力降級）確認 skill 整體仍站得住。**這是驗收，不是新一輪開放式壓測**——只記真的擋路、或會讓使用者拿到錯誤資訊的問題。
>
> 測試日期：2026-09-12

---

## 格 1：迴歸測試——首爾家庭真實草稿（v3/v4 沿用，輸出於 v5 概念下，未產出完整新檔）

### 跑了什麼
1. 對照 `trips/2026-10-seoul-family-v4/trip_context.json`、`materials/spots.json`、`materials/food.json`、`plan/05_transport.md`，用「16 個指名點跨 9 個 area（A–I）、市區真正自由天數僅 Day2/Day4 兩天」這個實際存在於 v4 資料裡的容量狀況，套用新版 `10_itinerary.md` 規則 8 的取捨優先序（已預約 > 草稿明確順序 > 素材庫友善度/熱門度）跑一次判斷。
2. 對照 `references/research_rules.md` §2.5.1（互動查詢型官方頁面降級）與 `references/intake.md`「草稿多版本」新增段落，用 v4 既有的天氣段落（`plan/10_itinerary.md` 天氣區塊，引用 Wanderlog 部落格）與 `trip_context.json` 的 `provenance`（old 區塊排除 星空圖書館／弘大 的判斷）做對照檢查，確認新文字本身是否清楚可依循（不要求 v4 舊產出回頭符合新規則，v4 產出於修正之前）。
3. 對 SKILL.md 的措辭修正做一次全庫搜尋比對一致性。

### 結果
- **規則 8 可執行**：套用到 v4 真實情境後，能得出具體、可寫進方案 A 開頭的取捨結論（優先序第 1 層鎖定南怡島包車日；第 2 層在「草稿寫在最前面」與「草稿給了獨立整天」兩種訊號打架時無法唯一判定，落到第 3 層）。第 3 層執行時發現一個實質缺口，見下方問題 1。
- **§2.5.1 文字清楚**：規則本身（連上但讀不到查詢結果時，不必先換路徑/換工具，直接引用 platform/blogger＋固定格式標記＋Google 搜尋連結）交代得很具體，套用到「首爾氣象廳日出日落資料抓不到數字」這個實際情境時，可以直接照樣寫出對應標記，沒有模糊空間。
- **intake.md 新增段落文字清楚**：套用到 v4 實際的 old 區塊（含「星空圖書館 or THE HYUNDAI SEOUL」「首爾塔／弘大」兩個新版沒提到的具體項目）可以明確得出「這兩項要主動列進引導式提問」的結論，規則本身沒有模糊到需要自己發明額外判斷標準。
- **SKILL.md 措辭修正已生效**，「1 套客製＋2 套部落客實走（地位不對等）」在 description 與內文皆已同步，與 `10_itinerary.md` 規則 5 一致。

### 發現的問題

**問題 1：規則 8 第 3 層「友善度評分/熱門度」引用了一個素材庫裡不存在的欄位**
- 檔案位置：`skills/travel-plan/references/sections/10_itinerary.md` 規則 8（本次修改項目）；對照 `skills/travel-plan/templates/spots.schema.json`。
- 問題：規則 8 寫「其餘依 09_materials.md 素材庫的**友善度評分/熱門度**排序，取分數較高者優先納入」，把兩者當同一件事並列。但實際 schema 只有 `friendliness`（1–5 分，量測的是無障礙／親子好走程度，例句如「石板路長、部分區域無遮蔽」），**沒有任何「熱門度」欄位**。
- 證據：`grep -rn "熱門度" skills/travel-plan/` 全庫只出現在敘述性文字裡（`09_materials.md` 兩處、`10_itinerary.md` 本條、`trip_profile.template.md` 一處），schema（`spots.schema.json`）與實際資料（`trips/2026-10-seoul-family-v4/materials/spots.json`）都只有 `friendliness.score`。實際套用到 v4 的 F/G/H（汝矣島／聖水洞／鷺梁津）三區時，唯一能排序的量化欄位就是 friendliness，但 friendliness 分數是「好不好走」不是「多受歡迎」，用它取代「熱門度」排序等於是 agent 自己重新定義了一個規則沒寫的替代標準。
- 影響：不算擋路（規則仍要求把取捨理由寫清楚，不會產生沉默的錯誤結果），但不同 agent 遇到這一步很可能各自發明不同的「熱門度」代理指標（有人用 friendliness、有人可能去查 Google 評論分數），導致同一份素材庫、同樣情境卻排出不同行程，喪失規則本該提供的一致性。
- 建議：擇一處理——(a) 規則 8 改成只講「友善度評分」，砍掉「熱門度」三字；或 (b) 給 `friendliness` 之外加一個明確定義的第二量化欄位。這個決定超出本輪驗收範圍，未動手修改，留給使用者決定方向。

**問題 2：「1 套客製＋2 套部落客實走」的措辭修正只同步到 SKILL.md，沒有同步到另外兩處仍描述舊版「三軸對稱三方案」的檔案**
- 檔案位置：`skills/travel-plan/references/sections/09_materials.md` 第 10 行；`skills/travel-plan/templates/trip_profile.template.md` 第 44、48 行。
- 問題：`09_materials.md` 第 10 行仍寫「三套方案（經典必去/深度在地/輕鬆慢遊）需要從同一批素材挑不同子集」；`trip_profile.template.md` 第 48 行的引導式提問「不回答會怎樣」仍寫「三套方案照預設三軸各自產出（經典必去/深度在地/輕鬆慢遊）」。這是舊版「三套對稱方案」的設計語言，跟 `10_itinerary.md` 規則 5 現行的「1 套客製（可選風格）＋2 套部落客實走（不分風格軸）」不一致。
- 證據：`grep -n "三套\|3 套" skills/travel-plan/templates/trip_profile.template.md skills/travel-plan/references/sections/09_materials.md` 兩檔皆命中舊三軸語言。
- 影響：`trip_profile.template.md` 是**直接秀給使用者看**的引導式提問文字，使用者若照這份問卷理解「行程風格傾向」欄位的作用，會得到跟實際產出不符的錯誤預期（以為不選風格會有三套對稱方案，但實際上方案 B/C 現在是找部落客文章，跟風格無關）。這屬於「會讓使用者拿到錯誤資訊」等級，值得記錄。
- 建議：這兩處不在本輪已修改的 4 項清單內，且不是打字錯誤等級（是設計語言未同步的範圍性修改），依約定不在本輪動手，留待下一輪處理。

---

## 格 2：全新情境——大阪 3 天 2 夜、幾乎空白輸入

輸出於 `trips/2026-10-osaka-minimal/`（`trip_context.json`、`progress.md`、`plan/05_transport.md`、`materials/spots.json`）。

### 跑了什麼
- 模擬使用者只給「我想去大阪玩 3 天 2 夜，10 月中」，無檔案。
- 依 SKILL.md 啟動順序：環境自檢（寫入 `progress.md`，`python3 --version` 實測 3.8.10 通過）→ 目的地門檻檢查（有給「大阪」，不觸發中止）→ 依 `intake.md` 備妥一批 3–5 題引導式提問（各附「不回答會怎樣」）→ 模擬使用者不再回覆，走「什麼都不想給」路徑，全部欄位依預設推斷並列入 `inferred_fields`。
- 產出 `trip_context.json`。
- 實際執行 05 交通（僅做 (a)(b) 兩塊）與 09 素材庫雛形（1 個 area、1 個景點），**真的上網查證**：關西機場到難波的南海電鐵/利木津巴士/計程車比較、ICOCA 退卡規則（官方 JR西日本 jr-odekake.net 查到明確公式：餘額－220円手續費＋500円押金）、道頓堀格力高看板（大阪市官方頁查證營業/點燈時間）。查不到的數字（如利木津巴士單程票價、Rapi:t 特急券加價）誠實標記 `[待確認]`，沒有編造。

### 結果
- 起步流程在全新目的地下**走得通，沒有卡住**：目的地門檻、引導式提問→預設推斷、`inferred_fields` 標記、`trip_context.json` schema 欄位，全部套用順利，跟首爾案例的操作方式一致，規格沒有因為換目的地而出現斷點。
- 實際上網查證環節正常運作：搜尋→開連結驗證→官方優先→查不到就標 `[待確認]` 的流程都跑得動，且過程中一次踩到自己的失誤（`spots.json` 一開始多加了一個 `_note` 欄位，因為 schema 是 `additionalProperties: false` 而作廢，改正後驗證通過）——這反而確認了 schema 的嚴格性是有效的，不是問題。
- 05/09 只做了部分小範圍雛形（05 只寫 (a)(b)、09 只 1 個 area 1 個景點），符合任務要求「跑 1-2 個主題證明流程通即可」的範圍，已在 `progress.md`/檔案內明確聲明這是雛形、非完整產出，未偽裝成完成品。

### 發現的問題
- 無。這格沒有找到擋路或誤導性的問題。

---

## 格 3：能力降級路徑——假裝無 Python、無子 agent（文件審查＋手動乾跑，未新建 trip）

### 跑了什麼
- 通讀 `references/portability.md`，逐項核對「無 Python」「無子 agent」兩條降級路徑是否都指名了明確的手動後備檔案、有沒有「規格預設有 script 可用、沒講清楚手動版怎麼做」的斷點。
- 挑 `references/checklists/validate_materials.md` 與 `references/checklists/scrub_check.md`，**不執行任何 python script**，純手動（grep + 逐行讀取 + 人工計數）對既有素材實際跑一次：
  - `scrub_check.md`：對 `trips/2026-10-seoul-family-v4/private/input/行程.md` 抽出訂房代號（26222508）、訂房人姓名（YEN）、去回程航班號（LJ734、KE2027）、門牌地址（太平路1街68-2）共 4 類實際出現的 token，逐一用 grep 搜尋 `trip_context.json`、`plan/*.md`、`materials/*.json`，**全部零命中**，判定通過。
  - `validate_materials.md`：對 `trips/2026-10-seoul-family-v4/materials/food.json` + `spots.json` 的「gwanghwamun」區做步驟 1、3、4、5、6、7 全套手動核對（tourist/local 各 3 家、類別橫跨 3 類、來源皆有深層 url、發布日期在 1 年內、有 rainy_day_ok true 的景點、`near_spot` 皆能在同區 `spots.json` 找到、列舉值皆合法），**全數通過**；步驟 2（跨日反重複）需要人工判斷「同一主食類型」，抽查全書 `signature` 欄位未發現超過 2 次的重複主食類型，判斷上需要一點主觀拿捏但可執行，不是卡在「其實還是要靠 script」的地步。
  - 也順手核對 `references/checklists/detect_agents.md`：純 shell 指令（`command -v` + 冒煙測試 + 字串判讀），本身就不依賴 Python，不受「無 Python」影響。

### 結果
- `portability.md` 的降級路徑**沒有斷點**：無 Python → 明確指到 `validate_materials.md`/`scrub_check.md`/`detect_agents.md`；無子 agent → 明確指到 `detect_agents.md` 判定 `ready` 數為 0 時直接序列模式，不需要再問使用者。三條鐵則（script 非必要路徑／script 失敗不中斷／script 只做校驗不做判斷）在兩份 checklist 實測中都成立。
- 兩份 checklist **確實可以純手動完成**，用 grep 與逐行讀取就能得出跟腳本一致的判定，沒有卡在「這步驟其實還是要靠 script 才做得到」的地方。

### 發現的問題
- 無阻斷性問題。步驟 2（跨日反重複）的「同一主食類型」判斷需要人工拿捏（例如「삼겹살烤肉」跟「삼겹살涮涮鍋」算不算同一類型），這是規則本質使然（語意判斷本來就比欄位比對模糊），不是這輪要處理的規格缺陷，僅記錄供參考，不列為問題。

---

## 總結論

三格全數通過，沒有發現擋路或會讓使用者拿到錯誤資訊等級的新問題出現在本次已修改的 4 項本身——4 項修正（`10_itinerary.md` 規則 8、`research_rules.md` §2.5.1、`intake.md` 新舊版段落、SKILL.md 措辭）逐一套用到真實資料都可執行、文字都清楚，沒有出現「模糊到我得自己發明規則之外的東西」的情況。

驗收過程中額外發現 2 個**不在本次 4 項修改範圍內**、因此按約定沒有動手的既有問題（詳見格 1）：
1. 規則 8 第 3 層引用的「熱門度」在 schema 裡不存在，只有語意不同的 `friendliness`。
2. `09_materials.md` 與 `trip_profile.template.md` 有兩處殘留舊版「三套對稱方案」措辭，其中 `trip_profile.template.md` 是直接面對使用者的引導式問卷文字，內容跟現行「1 客製＋2 部落客實走」設計不符。

這兩點都不影響「這輪測試完成」的結論——它們是範圍外的既有缺口，不是本次要驗收的 4 項修正本身失敗。**這個 skill 現在夠格說這輪測試完成**：本輪要驗收的目標（4 項修正落地、換目的地不卡、能力降級有退路）都已確認成立；上述 2 點留作下一輪處理的既知項目，不建議為了它們繼續本輪測試。
