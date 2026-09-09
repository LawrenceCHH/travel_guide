# checklist｜素材庫校驗（`validate_materials.py` 的 md 後備）

> 無 Python 3 執行環境時使用本檔，手動逐條核對 `materials/spots.json` 與 `materials/food.json`，
> 目標是得出與 `scripts/validate_materials.py` **相同的違規判定**。規則定義見 `references/sections/09_materials.md` §7.3。
> 對每一條，違規時記錄為 ERROR（阻斷，須修正才能進入下一步）或 WARN（提醒，可先標記待覆核後繼續）。

## 步驟 1：規則 1 — 每 area 觀光客 3 家 + 當地人 3 家，類別橫跨 ≥3 類
1. 打開 `food.json`，逐一列出每個 `area.id`。
2. 對每個 area，數 `picks[].audience == "tourist"` 的筆數，需 ≥ 3；數 `audience == "local"` 的筆數，需 ≥ 3。
3. 對每個 area，列出該 area 內出現過的 `category` 去重集合，需 ≥ 3 種不同值。
   **先排除步驟 7 判定為非法的值**——非法值不計入類別數，否則會與 `validate_materials.py` 得出相反判定。
4. 任一項不足 → **ERROR**：記錄「area X：tourist N 家（需≥3）」或「area X：category 只橫跨 N 類」。

## 步驟 2：規則 2 — 跨日反重複，同一主食類型全書最多 2 次
1. 篩出全書 `category` 為「正餐」或「小吃」的所有 picks。
2. 依 `signature`（招牌菜）或店名判斷是否為同一主食類型（如皆含「蔘雞湯」「雪濃湯」等關鍵字）。
3. 對每個主食類型做計數，若某類型全書出現次數 > 2 → **ERROR**：記錄「主食類型 X 出現 N 次：area.id 清單」。

## 步驟 3：規則 3 — sources 非空且 url 深層路徑非空
1. 對 `spots.json` 與 `food.json` 的每一筆物件，檢查 `sources` 陣列是否至少有 1 個元素 → 空的記 **ERROR**。
2. 對每個 `sources[].url`，把網址去掉 `https://domain` 部分，看剩下路徑是否為空（只剩 domain）→ 空的記 **ERROR**。

## 步驟 4：規則 4 — `published` 時效
1. 對每個 `sources[].published`，計算與「今天」相差天數。
2. 超過 365 天（約 1 年）→ **WARN**：標記「來源已超過 1 年，需覆核」。
3. 超過 730 天（約 2 年）→ **ERROR**：判不合格，不得直接引用。

## 步驟 5：規則 5 — 每 area 至少 1 個 `rainy_day_ok: true`
1. 對每個 `spots.json` 的 area，檢查 `spots[]` 中是否有至少一筆 `rainy_day_ok == true`。
2. 沒有 → **ERROR**：記錄「area X：無 rainy_day_ok 景點」。

## 步驟 6：規則 6 — `food.near_spot` 參照完整性
1. 先整理出 `spots.json` 每個 area 底下所有 `spots[].id` 的集合。
2. 對 `food.json` 每一筆 pick 的 `near_spot`，檢查是否存在於**同一個 area id** 的 spots id 集合中。
3. 找不到 → **ERROR**：記錄「food.area.pick_id：near_spot=X 找不到」。

## 步驟 7：規則 7 — 列舉值合法性
逐一核對下列欄位值是否落在合法清單內（清單見 `references/sections/09_materials.md` §7.1）：
- `spots[].category` ⊂ {文化古蹟, 自然景觀, 購物商圈, 網美打卡, 體驗活動, 室內歇腳}
- `spots[].audience` 陣列的每個值 ⊂ {tourist_must, local_favorite}
- `food[].category` ⊂ {正餐, 小吃, 咖啡甜點, 伴手禮}
- `food[].audience` ⊂ {tourist, local}
- `sources[].tier` ⊂ {official, platform, blogger}

有值不在清單內 → **ERROR**：記錄「欄位位置：值 X 不合法」。

## 步驟 8：彙總
把步驟 1~7 蒐集到的 ERROR / WARN 各自列成清單。**只要有任一 ERROR，本次素材庫視為未通過**，需修正後重跑本 checklist；WARN 可先記錄在 `progress.md`「待覆核的推斷值」區，不阻斷流程。
