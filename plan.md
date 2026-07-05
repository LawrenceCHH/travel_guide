# 🛠️ Config 欄位精簡計畫（第二輪）：同區塊欄位 → 單一自由文字字串

> 本檔覆蓋前一輪 plan.md（該輪已全數執行完畢：資訊架構藍圖化、food_preferences 雙軌欄位、
> 深層連結引用規範、orchestrator 深度模式、README 同步，詳見 git log）。
> 這一輪只處理**設定檔欄位精簡**與相應 prompt 的解析規則，不重動上一輪已完成的章節結構/ 引用規範 / 美食公式。

## 🎯 使用者這次要解決的問題
1. `travel_config.yml` 有些地方**同一個邏輯區塊被拆成太多細欄位**（例如出發國家/出發機場/目的地/抵達機場/航空公司 5 個欄位），使用者填起來麻煩。
2. 目標：把「同一區塊」的內容合併成**一個自由文字字串**，Agent 自己解析裡面的子項目。
3. 沿用 `food_preferences` 已經驗證過的模式：**留空 → 自動啟動預設/通用模式**；**有填 → 解析內容做客製化**。這個「留空=預設、填寫=客製」的邏輯這次要推廣到其他可合併的區塊，而不是只有美食欄位獨有。

---

## 🔍 現況盤點（本輪要動的欄位）

| 現況欄位 | 問題 | 本輪處理 |
|---|---|---|
| `departure_country` + `departure_airport` + `destination` + `arrival_airport` + `airline`（5 個欄位） | 同一件事「行程路線」被拆成 5 格 | **合併成 1 個欄位 `trip_route`**（自由文字，Agent 解析出 5 個子變數） |
| `target_year` | 表面上與 `travel_dates.start_date` 重複，但實際語意是「檢索資訊要鎖定哪一年」，與「旅遊實際日期」是兩件事（例：旅遊橫跨兩個年份、或想額外查詢隔年新制） | **不刪除，改為選填 + 有預設推導**：留空時推導自 `travel_dates` 涵蓋的年份（跨年行程則涵蓋頭尾兩年），有填時以填寫值為準（覆寫推導）——比照 `food_preferences` 的「留空預設、填寫覆寫」邏輯，比直接刪除更貼合本輪精神 |
| `preferences.duration_days` | 與 `travel_dates` 的起訖日期重複，且**目前沒有任何 prompt 實際讀取這個欄位**（純記錄用途） | **直接刪除，不新增替代變數**：不引入 `{旅遊天數}`，因為沒有 consumer 會用到它，屬於未使用的死變數；行程章節本來就會自行從 `travel_dates` 推算天數規劃 |
| `companions.total_count` + `companions.relationship_type`（巢狀 2 子欄位） | 同一件事「同伴資訊」被拆成巢狀 2 格 | **合併成 1 個欄位 `companions`**（自由文字，型別從 object 改 string） |
| `travel_dates.start_date` / `end_date` | 兩個子欄位描述同一件事「日期區間」，但都是**結構化日期**，不是「同一資訊被拆碎」的那種冗餘 | **維持結構化，不合併**（原因見下方「不合併的部分」） |
| `telecom_carrier` / `language` / `tone_style` / `preferences.hotel` | 各自已經是單一原子欄位，不存在「同區塊拆碎」問題 | **維持不變** |
| `preferences.food_preferences` / `preferences.notes` | 已經是單一自由文字欄位（上一輪剛做好的設計） | **維持不變**，作為本輪其他欄位比照的範本 |

### ⚠️ 不合併的部分（需要 Opus / 使用者確認的設計判斷）
1. **`travel_dates` 保持結構化 `start_date` / `end_date`，不與 `trip_route` 或其他欄位合併成一句話。**
   理由：日期是全份規劃書排程正確性的根基（機票時間、每日行程順序、天數計算都靠它），
   用結構化 ISO 日期可避免 Agent 解析自然語言日期時算錯年份/日期區間。這與「同一區塊拆碎」的病灶不同——
   起訖日期是精確數值，不是被過度拆分的敘述資訊。
2. **`trip_route` 中的「目的地」不適用「留空 → 預設模式」邏輯。**
   食物偏好留空可以合理啟動「多元自主蒐集」；但目的地留空時 Agent **無法自主發明一個目的地**。
   因此規則訂為：若 `trip_route` 整欄留空、或內容中無法辨識出目的地，Agent 必須**停止並提示使用者至少填寫目的地**，
   不得憑空規劃。這是本次唯一不套用「留空即自動預設」的必填例外，需要明確標註避免歧義。
   - **（Opus 覆核後補強）** 此停止規則須給出**逐字固定句**（而非改寫式指令），LLM 對逐字拒絕句的遵從度遠高於意譯指令，例如：
     `「trip_route 未指定可辨識的目的地，請至少補上目的地後再執行規劃。」` + 明確加註「禁止自行發明或臆測目的地」。
   - **（Opus 覆核後補強）** 此檢查必須放在 **Variable Extraction 階段、任何 WebSearch/派工動作之前**——
     對 orchestrator 尤其關鍵：一旦主管把任務派給子 agent 後，流程已是非互動式的並行執行，
     沒有「向使用者提問」的時機，因此主管必須在**派工前**就完成這個門檻檢查並中止，而不是任由某個子 agent 事後才發現目的地缺失。
3. **`telecom_carrier` 首次被賦予「留空 = 預設模式」語意**（目前設計中它一直被當作必填）。
   留空時 Agent 只比較當地 eSIM/SIM/WiFi 通用方案，不做特定電信商的漫遊資費比較。此為順著本輪精神的
   小幅擴充，非嚴格「合併欄位」範疇，一併列入，供 Opus 評估是否要做。

---

## 📐 新版 `travel_config.yml` 結構（示意）

```yaml
# ✈️ AI 旅遊規劃系統本地設定檔 (隱私保護)

# 行程路線（必填，至少要能看出目的地）：用一段自然語言描述出發地、出發機場（含航廈）、
# 目的地、抵達機場（含航廈）、去回程航空公司即可，不用分開填欄位。
# 若省略機場航廈或航空公司等細節，Agent 會自動查詢當前最常用/合理的選項並在規劃書中註明推論依據。
trip_route: |
  從台灣桃園國際機場 (TPE) T1 出發，前往韓國首爾仁川國際機場 (ICN) T2。
  去程搭乘真航空 (Jin Air)，回程搭乘大韓航空 (Korean Air)。

# 旅遊日期（必填，請用明確日期 YYYY-MM-DD，避免自然語言日期造成誤判）
travel_dates:
  start_date: "2026-10-15"
  end_date: "2026-10-18"

# 檢索限定年份（選填）：限定 Agent 查詢資訊時鎖定哪一年的最新規定/票價/匯率。
# 留空時自動推導自上方 travel_dates 涵蓋的年份（跨年行程則兩個年份都納入檢索）；
# 若旅遊日期橫跨年底年初、或想額外查詢隔年新制，可在此明確覆寫。
target_year: ""

# 通訊與語言偏好
telecom_carrier: "中華電信"          # 選填；留空則只比較當地 eSIM/SIM/WiFi 通用方案，不做電信商漫遊比較
language: "繁體中文 (zh-TW)"          # 規劃書輸出語言

# 規劃書寫作與排版風格偏好
tone_style: "台灣、繁體中文用語"

# 同伴資訊（選填，一段自然語言描述人數、年齡、關係即可）。
# 留空時 Agent 會以「一般成人旅客」為假設進行規劃，仍會產出同伴友善度評分，但不會有特殊防雷加權。
companions: |
  4 位成人的家庭旅遊（31、33、50+、50+ 歲）。

# 特殊交代與個人偏好
preferences:
  hotel: "新首爾飯店 New Seoul Hotel Myeongdong"
  # 美食偏好（選填）：辣度、想吃品類、忌口都可自由寫成一段話。
  # 留空時 Agent 會自動蒐集多元類別美食，適合不熟該國的旅客參考。
  food_preferences: |
    不能吃辣；避免生食與內臟。
  notes: |
    1. 成員與步調：...
    2. 航班時間：...
    ...
```

被刪除的欄位：`departure_country`、`departure_airport`、`destination`、`arrival_airport`、`airline`（併入 `trip_route`）、
`companions.total_count`/`companions.relationship_type`（併入 `companions` 字串）、
`preferences.duration_days`（無任何 prompt 讀取，純冗餘記錄欄位，直接刪除、不新增替代變數）。

保留但改為選填的欄位：`target_year`（留空時推導自 `travel_dates` 涵蓋年份，填寫時以填寫值覆寫推導）。

---

## Step 1 — 改寫 `travel_config.yml`
- [ ] 依上方結構重寫，內容資料本身不變（首爾家庭旅遊該次行程的實際資訊），只改變欄位形狀。
- [ ] `trip_route` 用自然語言完整保留原本 5 個欄位資訊（出發地/出發機場含航廈/目的地/抵達機場含航廈/去回程航空公司）。
- [ ] `companions` 用自然語言保留原本人數與關係型態資訊。
- [ ] `target_year` 保留原值 `"2026"`（此份實際設定檔原本就有明確填寫，維持填寫值，不需要改成留空）。

## Step 2 — 改寫 `travel_config_template.yml`
- [ ] 同步新結構，`trip_route` 與 `companions` 附上清楚的填寫範例與「必填/選填＋留空行為」註解。
- [ ] `trip_route` 註解需明確標註「必填，至少要看得出目的地」。
- [ ] `companions` 註解標註「選填，留空 = 一般成人旅客假設」。
- [ ] `telecom_carrier` 註解補上「選填，留空 = 只比較通用 eSIM/SIM/WiFi」。
- [ ] `target_year` 註解標註「選填，留空 = 推導自 travel_dates 涵蓋年份（跨年行程涵蓋頭尾兩年）；填寫則覆寫推導」，範本版留空示範。

## Step 3 — 更新 `prompt_generate_trip.md`
- [ ] **Variable Extraction** 區塊改寫（此區塊即為門檻檢查的執行位置，須在任何 WebSearch 之前）：
  - `{出發地}/{出發機場}/{目的地}/{目的機場}/{航空公司}` ← 從 `trip_route` 自由文字解析出。
    **解析時第一步先確認能否辨識出目的地**：若 `trip_route` 整欄留空或無法辨識目的地，
    立即輸出逐字句：`「trip_route 未指定可辨識的目的地，請至少補上目的地後再執行規劃。」`，
    並**停止後續所有步驟**（不得繼續 WebSearch 或撰寫任何章節），嚴禁自行發明或臆測目的地。
    其餘細節（航廈、航空公司）缺漏時，可自主查詢合理預設值並在規劃書中註明依據，不觸發停止。
  - `{目標年份}` ← 若 `target_year` 有填寫，直接採用；**留空時**推導自 `travel_dates` 涵蓋的年份
    （若旅遊日期橫跨年底年初，頭尾兩個年份都納入檢索範圍）。
  - `{同伴資訊}` ← 從 `companions` 自由文字解析（原本是讀 object，現在讀字串）；**留空時**以一般成人旅客為假設，
    仍產出同伴友善度評分但不做特殊防雷加權。
- [ ] （不新增 `{旅遊天數}` 變數：`duration_days` 目前沒有任何 prompt 讀取，屬純記錄冗餘欄位，直接刪除即可，
  行程章節本來就會自行從 `travel_dates` 起訖日期推算天數與排程，不需要額外變數。）
- [ ] 新增小節「🧩 設定檔解析與預設模式規則」，統整上述 `trip_route`／`target_year`／`companions`／`telecom_carrier`
  的「留空預設、填寫覆寫／客製」規則，並清楚標註**目的地是唯一不適用留空預設、必須停止並詢問使用者的例外**。
- [ ] 檢查全文其餘引用 `{目標年份}`、`{同伴資訊}` 等變數的地方（時效性規則、行程防雷段落等）不需改字面，因為變數名稱不變，只有推導來源改變。

## Step 4 — 更新 `prompt_update_trip.md`
- [ ] 套用 Step 3 的 Variable Extraction 改寫（**不含** `{旅遊天數}`，該變數已確定不新增）。
- [ ] 套用 Step 3 的「設定檔解析與預設模式規則」小節。
- [ ] 檢查「行程與偏好微調」一節，若使用者改了 `trip_route`（換目的地/航班）或 `companions`，比照既有 `{美食偏好}` 變更邏輯納入判斷條件。

## Step 5 — 更新 `orchestrator/prompt_orchestrator.md`
- [ ] 套用相同 Variable Extraction 改寫。
- [ ] **（Opus 覆核後補強，本檔為關鍵風險點）**：目的地門檻檢查必須放在「第一步：讀取與拆解」，
  且明確寫成**派工前的硬性關卡**——主管一旦完成並行派工，流程即為非互動式，沒有機會事後再向使用者確認；
  若 `trip_route` 無法辨識目的地，主管必須在派工前輸出停止句並中止整個 orchestrator 流程，不得派出任何子 agent。
- [ ] 派工說明中「完整 `travel_config.yml` 內容」不變（子 agent 仍拿到全檔），但主管解析出的變數清單需同步更新。

## Step 6 — 微調 `orchestrator/prompt_section_worker.md`
- [ ] 公式 C「依 `companions` 進行防雷檢驗」旁補一句：若 `companions` 留空，以一般成人旅客為假設。
- [ ] 其餘不動（本檔本來就不直接做 Variable Extraction，只接收主管轉交的已解析變數）。

## Step 7 — 更新 `README.md`
- [ ] **（Opus 覆核後補強，需精準定位）**：README 第 21 行目前寫「包含您的出發地、目的地、起訖機場、航空公司、
  旅遊日期、電信商、同伴資訊、**寫作風格偏好 (`tone_style`)**、**美食偏好 (`preferences.food_preferences`)** 以及備註偏好」，
  這句話仍是舊欄位形狀的敘述，必須重寫為新形狀（`trip_route` 一段話涵蓋出發地/機場/目的地/航空公司；
  `companions` 一段話；`target_year` 選填），否則會與新版 config 矛盾。
- [ ] 設定檔說明段落，反映欄位精簡後的樣貌：`trip_route`（必填，一段話涵蓋出發地/機場/目的地/航空公司）、
  `companions`（選填一段話）、`telecom_carrier`（選填）、`target_year`（選填）。
- [ ] 補一句總原則說明：「本系統的欄位設計原則是——填越少，Agent 自動補的越通用；填越細，規劃越客製化」，
  呼應 `food_preferences` 與新欄位一致的邏輯。

---

## ✅ 驗收檢查表
- [ ] `travel_config.yml` / `travel_config_template.yml` 不再有 `departure_country`／`departure_airport`／
      `destination`／`arrival_airport`／`airline`／`companions.total_count`／
      `companions.relationship_type`／`preferences.duration_days` 這些欄位名稱。
- [ ] `target_year` 保留（改為選填語意），未被刪除。
- [ ] 兩份設定檔新增 `trip_route`（string）與 `companions`（string）。
- [ ] 三份 prompt（generate / update / orchestrator）Variable Extraction 皆改為從 `trip_route` 解析五個路線變數、
      `{目標年份}` 支援「留空推導 / 填寫覆寫」、從 `companions` 解析同伴資訊；**不含**新增的 `{旅遊天數}` 變數。
- [ ] 三份 prompt 皆含「設定檔解析與預設模式規則」（或等效小節），且**明確排除目的地的「留空預設」**，
      改為輸出逐字停止句並中止流程；`prompt_orchestrator.md` 的門檻檢查明確標註為「派工前」的硬性關卡。
- [ ] `travel_dates` 仍保持結構化 `start_date`/`end_date`，未被併入自由文字。
- [ ] README 第 21 行（設定檔欄位列舉句）已重寫為新欄位形狀，且反映「填越少越通用、填越細越客製」的整體原則。

---

## 📝 Opus 審視結論（已於本輪納入上述修正）
- **採納**：`target_year` 不刪除，改為選填 + 留空推導（跨年行程涵蓋頭尾兩年）／填寫覆寫。
- **採納**：不新增 `{旅遊天數}` 變數（`duration_days` 本來就沒有任何 prompt 讀取，是死欄位，直接刪除即可）。
- **採納**：目的地缺失的停止規則改為逐字固定句 + 明確放在 Variable Extraction／派工前的門檻位置（尤其 orchestrator）。
- **採納**：README 需精準修正第 21 行，避免與新版 config 矛盾。
- **維持原案**：`trip_route`/`companions` 合併、`travel_dates` 保持結構化、`telecom_carrier` 留空預設、
  不處理舊格式相容（config 為個人 gitignored 檔案，單人使用，無需遷移）。
- Opus 總評：「approve with the fixes above」——整體切分（結構化數值 vs. 敘述性資訊該不該合併的判準）正確，
  不算過度工程化，上述修正已納入本計畫。
