# 09｜素材庫

## 目的
建立**可重組**的景點與美食原始素材，與 `10_itinerary.md` 的「組合成品」分離。改行程不用重查素材，一份素材可組出 3 套不同的行程方案。

**這份素材庫是整個 skill 的核心產出，`10_itinerary.md` 只是其中一種用法（參考草案）。** 使用者拿到 `materials/` 後，可以直接照 `10_itinerary.md` 的建議走，也可以自己以半天為單位重組，或拿去跟其他 agent 討論深化——素材庫本身要能撐起這些不同用法，重點不是把某一套行程排到滴水不漏，而是讓景點/美食資訊本身**最新、正確、彼此的空間關係清楚**（見下方 `nearby_areas`／`nearby_spots`），這樣不管誰來組行程都不會把實際上很遠的地方誤以為很近。

## 為什麼素材庫與行程安排要分離
- **成本結構不同**：素材庫是檢索密集型工作（找景點、找美食、驗證來源），行程安排是組合密集型工作（排序、分區、算 buffer）。混在一起會導致每改一次行程順序就要重新檢索一次。
- **重組彈性**：三套方案（經典必去/深度在地/輕鬆慢遊）需要從同一批素材挑不同子集、給不同權重，若素材與行程綁死在同一份文件，無法在不重查的情況下產生三套差異化方案。
- **校驗可獨立執行**：§7.3 的硬約束（類別覆蓋、反重複、參照完整性等）只需針對素材庫本身校驗一次，不必每套行程各驗一次。

## 前置依賴
- `trip_context.json`：`destination`
- `05_transport.md`：區域可達性與交通樞紐資訊，用於劃分 `areas`
- `01_flight_stay.md`：`stay.area`，作為素材分區的起點區域

## 必須產出的檔案
- `trips/{trip}/materials/spots.json`（依 `templates/spots.schema.json`）
- `trips/{trip}/materials/food.json`（依 `templates/food.schema.json`）

## §7.1 Schema 欄位說明與合法列舉值

完整欄位型別與必填規則見 `templates/spots.schema.json`／`templates/food.schema.json`（draft-07，可直接當範例參考，內含 `examples`）。**JSON 沒有註解，因此合法列舉值定義在本檔，資料檔本身不重複寫值定義：**

| 欄位 | 合法值 |
|---|---|
| `spots[].category` | `文化古蹟`／`自然景觀`／`購物商圈`／`網美打卡`／`體驗活動`／`室內歇腳` |
| `spots[].audience` | `tourist_must`／`local_favorite`（陣列，可並列） |
| `food[].category` | `正餐`／`小吃`／`咖啡甜點`／`伴手禮` |
| `food[].audience` | `tourist`／`local`（單值） |
| `sources[].tier` | `official`／`platform`／`blogger`（定義見 `research_rules.md` §5） |

任何不在上表清單內的值視為不合法（由 `validate_materials.py`/其 checklist 後備檢查，見 §7.3 第 7 條）。

欄位語意補充：
- `spots[].id` / `food[].id`：英數與底線組成的短代碼，供跨檔參照（`food.near_spot` → `spots.id`）。
- `spots[].booking_required`：是否需事先預約，會被 `01_flight_stay.md` 的訂位清單引用。
- `spots[].rainy_day_ok`：是否可作為雨天/公休/排隊過長的 Plan B，會被 `10_itinerary.md` 的每半天 Plan B 規則引用。
- `food[].near_spot` / `walk_min`：定義這家美食「掛在哪個景點旁邊」與步行時間，是 `10_itinerary.md` §層級呈現（區域→景點→旁邊美食）的資料基礎。
- `areas[].nearby_areas`：記錄大區域之間的距離關係（`area_id`／`travel_min`／`mode`），**避免組行程時把實際上很遠的兩個大區域誤排在同一個半天/整天**。**選填、非窮舉**——只記實際會用到、有查證依據的鄰近關係即可，不必列出跟所有其他 area 的配對；`travel_min` 必須可回溯到 `05_transport.md` 已查證的資料，不得憑空估算。
- `spots[].nearby_spots`：記錄同一 area 內走路可達的其他景點（`id`／`walk_min`）。**選填、非窮舉、單向**——不要求兩個景點互相登記對方，寫的人挑重要的記即可，不必為了對稱而互相補登。
- `spots[].best_time_notes`：只有時間敏感型景點（看日出/日落、潮汐等）、且查資料時剛好看到具體建議時段才填，**不必為每個景點特地去查一次有沒有最佳時段**。

## §7.2 輸出約定（六條，取代原本的「受限 YAML 子集」）

JSON 本身沒有歧義，但 **diff 品質靠約定維持**：

1. **欄位順序固定**，依 schema 宣告順序輸出，不得因重新產生而重排。
2. **巢狀不超過 3 層**（root → areas → spots/picks → 物件欄位）。
3. `sources` 陣列**每個來源物件寫成一行**（不換行展開），減少改動時的行數擾動。
4. 縮排 2 空格，UTF-8，**不轉義非 ASCII**（`ensure_ascii=false`），中文與韓文直接可讀。
5. 檔尾保留換行。
6. 修改既有素材時**只動該筆物件**，不重排、不重新格式化整檔。

這組約定由 `scripts/render_materials.py` 在寫檔（含 `--rewrite` 正規化模式）時強制執行；無程式執行環境時，agent 手動編輯需自行遵守，`references/checklists/validate_materials.md` 的步驟可用來事後檢查是否符合。

## §7.3 硬約束（七條，由校驗執行）

1. 每個 `area` 的 `food.picks` 必須含**觀光客 3 家 + 當地人 3 家**（`audience` 各 3 筆），且 `category` 橫跨至少 3 類。
2. 跨日反重複：同一主食類型（依 `signature`/店名判斷是否為同一主食類別，如都是雪濃湯類）全書最多出現 2 次。
3. 每筆（`spots`/`food` 皆同）必須有非空 `sources`，且每個 `sources[].url` 去掉 domain 後路徑不可為空。
4. `sources[].published` 距今超過 1 年要標記（WARN），超過 2 年判不合格（ERROR）。
5. 每個 `area` 的 `spots` 中至少 1 個 `rainy_day_ok: true`（供 `10_itinerary.md` 的 Plan B 使用）。
6. `food.picks[].near_spot` 必須存在於 `spots.json` 的**同一 area** 中（參照完整性）。
7. 所有列舉欄位（見 §7.1 表）的值必須落在合法值清單內。
8. **`areas` 必須覆蓋 `trip_context.named_musts` 涉及的全部地理區域**，不得只做最低限度（schema 的 `minItems: 1` 只是格式下限，不是完成標準）。若受限於執行時間無法逐區建檔，**不得靜默省略**：未覆蓋的區域要在 `progress.md` 列出清單與原因，且 `10_itinerary.md` 引用該區域的指名景點時必須明確標註「未依 09 規格建檔，直接沿用使用者草稿原文，未經來源查證與友善度評分」——不可讓成品外觀上看起來與正式建檔的區域一樣完整。
9. `areas[].nearby_areas[].area_id` 與 `spots[].nearby_spots[].id` 若有填，參照對象必須真實存在（前者存在於同一 `areas` 陣列、後者存在於同一 area 內）——這是唯一的機械檢查，**不檢查也不要求完整性/對稱性**（有沒有填齊、A 記了 B 但 B 沒記 A，都不算違規）。

前八條規則的機械執行由 `scripts/validate_materials.py` 完成，輸出區分 ERROR（阻斷）/WARN（提醒但不阻斷）；第 8 條是覆蓋範圍規則，`validate_materials.py` 不做地理覆蓋判斷，需 agent 自行對照 `trip_context.named_musts` 檢查，或使用 `references/checklists/validate_materials.md` 的等效手動步驟。

## 必須回答的問題清單
- 這個大區域要分成哪幾個 `area`（依 §7.1 與 05 的交通樞紐劃分，通常以捷運站/商圈為單位）？
- 每個 area 裡，哪 3 個是觀光客必去、哪 3 個是當地人推薦？
- 每個 area 有沒有至少一個雨天也能去的地方？
- 這家美食實際上是「掛」在哪個景點旁邊、走過去要多久？

## 檢索指引與來源要求
- 全部依 `references/research_rules.md`，一般等級。景點/美食推薦以 `tier: blogger` 近一年實測為主，開放時間/門票金額等規範性資訊優先 `tier: official`/`platform`。
- **發掘管道依 `research_rules.md` §9 的兩階段流程**：`areas`/`spots` 的候選優先來自「使用者所在國旅人」寫「目的地國」的遊記（§9.1）；`food.picks` 的候選改用目的地國當地人常用的地圖/搜尋服務找，並刻意跨不同分類取樣以避免美食同質化（§9.2，韓國已驗證用 `search.naver.com` 整合搜尋）。找到候選後仍要依 §1/§2 找到可引用的深層文章來源，地圖面板本身不可當 `sources`。
- **飲食限制沿用既有的 `derived_constraints` 機制**，不另立專屬欄位：使用者若明講飲食限制（不吃辣、素食、過敏原⋯），依 `intake.md` 寫成一句 `trip_context.derived_constraints`，跟「紅眼班機」「末半天可用時數」同一個陣列、同等對待，選材時自然納入考慮即可。沒講就不必主動找話題去問，也不必自行加上使用者沒要求的限制——維持 §9.2 的熱門度/跨分類取樣邏輯就好。
- **不建同伴體力/地形篩選機制**：`party.mobility_notes` 僅作為使用者原話的參考紀錄，09/10 不需要、也不應該依地形難度篩選或排序景點與美食。

## 完成判準 checklist
- [ ] `spots.json`／`food.json` 皆通過 schema 驗證（必填欄位齊全、列舉值合法）
- [ ] §7.3 九條硬約束全數通過（或已知違規已標記並知會使用者）
- [ ] `areas` 覆蓋 `trip_context.named_musts` 的全部地理區域，未覆蓋者已在 `progress.md` 列出清單與原因（§7.3 第 8 條）
- [ ] 輸出符合 §7.2 六條約定（欄位順序、巢狀 ≤3 層、`sources` 單行、2 空格縮排、`ensure_ascii=false`、檔尾換行）
- [ ] `food.near_spot` 全數可在同 area 的 `spots` 中找到
- [ ] 若有填 `nearby_areas`／`nearby_spots`，參照對象真實存在（不要求填滿、不要求對稱）

## 常見錯誤
- 觀光客/當地人各 3 家湊不滿，用重複店家充數。
- `rainy_day_ok` 全部留 `false`，導致該 area 沒有 Plan B 可選。
- `near_spot` 填了別的 area 的景點 id，造成參照失敗。
- 手動編輯 JSON 時重新格式化整檔，導致 diff 大量無意義變動。
- 把 `nearby_areas`／`nearby_spots` 當成硬性要求，花時間去建完整的兩兩配對距離矩陣——這兩個欄位是選填、非窮舉，只記有查到、會用到的即可。
- `nearby_areas.travel_min` 自己憑感覺估一個數字，沒有回溯到 `05_transport.md` 的查證資料——這等於把「避免 AI 幻覺距離」的欄位本身做成幻覺。

## script 呼叫方式（可選加速器）

有程式執行能力時（見 `references/portability.md`），從 skill 資料夾根目錄執行：

```bash
python3 scripts/validate_materials.py --spots trips/{trip}/materials/spots.json \
                                      --food  trips/{trip}/materials/food.json
# exit 0 = 通過；1 = 有違規（清單分 ERROR / WARN）；2 = 執行失敗

python3 scripts/render_materials.py --spots trips/{trip}/materials/spots.json \
                                    --food  trips/{trip}/materials/food.json \
                                    --out   trips/{trip}/materials/materials.md
python3 scripts/render_materials.py --spots ... --food ... --rewrite   # 原地正規化 JSON（強制 §7.2 約定）
```

**script 不是必要路徑。** 無法執行、執行失敗或無 Python 時，一律改走 `references/checklists/validate_materials.md`，並在 `progress.md` 記錄「本次以 checklist 校驗」。
