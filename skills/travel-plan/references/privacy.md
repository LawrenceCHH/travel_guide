# 隱私分層：什麼進版控

> 對應計畫書 §5 全部。

## 原則

> **版控的是「知識」，不版控的是「身分」。**
> 使用者提供的原始資訊一律不進版控；agent 產生的**去識別化 `trip_context.json`** 才進版控。所有下游產出只引用 `trip_context`，不回填原始值。

## 去識別化規則表

> 以下欄位值皆為**虛構示意**，不代表任何真實使用者資料。

| 原始欄位（範例值） | 進版控的形式 | 理由 |
|---|---|---|
| 訂房確認號（如 8 位數字） | **刪除** | 可被用來查詢或變更他人訂房 |
| 訂房人姓名 | **刪除**（或改稱「成員 A」） | 直接識別 |
| 航班號（去程／回程） | **刪除** | 可反查訂位；規劃本身用不到 |
| 起降時刻（如 `01:25→05:00`、`16:10`） | **保留** | 首尾 buffer 計算的必要輸入 |
| 航空公司 | **保留** | 查行李規範必需，不具識別性 |
| 機場含航廈（如 `TPE T1` / `ICN T2`） | **保留** | 通關流程必需 |
| 飯店名（單獨） | **保留** | 公開可查的商業名稱，單獨出現不具識別性，不指向特定人 |
| 門牌地址（含樓層/房號） | **改為「區域 + 最近車站」** | 精確地址可定位到建築本身；風險點是「飯店名/地址＋真實姓名＋入住日期」疊在一起才會揭露真人在哪個時間點出現在哪個確切地點，姓名已獨立必刪，足以打斷這個疊加，但門牌仍比商業名稱更精確，保守處理 |
| 房型與訂單人數 | **改為結構描述**（如「4 位成人、1 房」） | 規劃需要的是限制條件不是訂單 |
| 聯絡方式、Email、電話 | **一律刪除** | — |

## `trip_context.json` 產出範例

> **虛構資料**，僅示意結構，不對應任何真實行程。完整 schema 見 `templates/trip_context.schema.json`。

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

`derived_constraints` 是刻意保留的自然語言欄位——它裝的是**推論結果**（例如紅眼班機該怎麼排），不是個資，而且下游主題最需要的就是這幾句。`inferred_fields` 列出哪些值是推斷來的，直接餵給 `progress.md` 的「待覆核的推斷值」區塊。

## 執行機制（五點）

1. `.gitignore` 加入 `trips/*/private/`。
2. agent 產出 `trip_context.json` 後，**第一次 commit 前必須讓使用者過目確認**——這是人工關卡，不可跳過，不論當下環境是否有 git。
3. `scripts/scrub_check.py`（有程式執行時）：從 `private/` 的原始輸入抽出專有字串（確認號、姓名、航班號、門牌地址等 token），掃描所有**將進版控的檔案**是否含這些字串，命中即報錯。無程式執行時走 `references/checklists/scrub_check.md` 手動比對。
4. **個人化成品放 `private/personal/`**：使用者旅行時當然想看到飯店名與航班號。作法是 `plan/` 保持抽象可版控，agent 另外用 `plan/` + 原始輸入合成一份個人化版本放進 `private/personal/`，不進版控。
5. `progress.md` 一律只引用 `trip_context` 層級的值，不得寫入原始個資。

## `scrub_check.py` 呼叫方式（可選加速器）

```bash
python3 scripts/scrub_check.py --input trips/{trip}/private/input/* \
                               --targets-dir trips/{trip}
# 或指定個別檔案：--targets trips/{trip}/trip_context.json trips/{trip}/plan/*.md
# exit 0 = 未發現外洩；1 = 命中（逐筆列出檔名、行號、token 類別）；2 = 執行失敗
```

`--targets-dir` 會遞迴掃描目錄下的 `.md` / `.json` 並自動跳過 `private/`。無程式執行能力時改走 `references/checklists/scrub_check.md` 手動比對——**這一步不可省略**，只是換方式做。

## 無 git 環境的隱私意義

網頁版沒有 git，但分層依然有價值：使用者會下載並可能分享 `plan/` 的內容，而 `private/` 明確標示為不可分享。skill 輸出「接續包」清單時（見 `references/progress_protocol.md`）要標明哪些可分享、哪些不可分享，讓使用者在沒有 `.gitignore` 強制執行的環境下，仍知道哪些檔案不該貼到公開場合。
