# `index.html` 前端實作紀錄 (Implementation Log)

> 首爾秋日漫遊手帳單頁 App。**事實來源**：`travel_韓國首爾_edited.md`（價格/電話/連結/政策照抄，不得竄改）。**設計準則**：`web_design_preference.md`（侘寂綠、行動核心一體化、540px 置中卡片、單一 DOM、零外部依賴、可離線開啟）。
> 本檔記錄已完成的功能與關鍵設計決策，供後續維護參考。

---

## 現況架構

- **分頁順序**（單層導覽 + 左右滑動）：`overview · preparation · airport · spots · food · useful · emergency`。
- **核心 JS**（`<script>`）：`switchSection` / `goBack` / `jumpToSpot` / `jumpToFood` / `toggleFoodArea` / `scrollToAnchor` / `setupSwipeNavigation`，全部 `window.` 掛載。
- **技術鐵則**（每次改動都不得破壞）：單一檔案、零外部依賴、可離線開啟（全 inline SVG，無 CDN/字型/圖片/API）；`localStorage` 全包 try-catch；行內事件函式掛 `window`；結構控制項禁 emoji；6 個 `food-area` id 唯一。

---

## 已完成功能

### 1. 底部持久快捷列（4 顆）
`緊急撥號（emphasis）· 回上頁 · 回總覽 · 回頂`，inline SVG line-icon、觸控區 ≥44px、窄手機不爆版。

### 2. 回上頁（瀏覽歷史 back）＋捲動位置還原
- 記憶體堆疊 `sectionHistory`，元素為 `{ id, y }`（y = 離開分頁當下的 `window.scrollY`）。
- `switchSection(event, id, opts)` 第三參數：`record`（是否記錄，預設 true）＋ `scrollTo`（數字=還原到該 y／`false`=不動捲動，供 jump 用／預設=回頂 `0`）。
- `goBack()` pop `{id,y}` 後 `switchSection(null,id,{record:false,scrollTo:y})`；空堆疊 no-op。
- **前進導覽一律落在新分頁頂端**（順帶修好 nav/滑動落在半空的問題）。

### 3. 左右滑動切換分頁（touch）
- 有效水平滑動：`|dx|>60 && |dx|>2*|dy|`；左滑→下一分頁、右滑→上一分頁，到頭尾不循環。
- **避讓橫向捲動容器**（`.nav-menu / .anchor-chip-row / .food-index-legend / .food-actions` 及任何 overflow-x auto/scroll 祖先），防手勢衝突。

### 4. 美食內容單一來源
美食清單（6 區 × 5 家 `details.food-item`）**只存在「美食」分頁**；景點卡改放「本區美食 →」跳轉列（`jumpToFood`）。與美食區底部「散步路線 ↗」形成雙向鏡像導覽。

### 5. 美食區塊互動（現行定案）
每區 `.food-area` 預設**收合**，三段式：
- **標題 `.area-head`**（accordion header，點了原地展開/收合）：`景點名 + 「N 家」chip + 招牌店名預覽`（預覽僅收合態顯示）；右側圓形 chevron 展開旋 180°；展開時整條轉 `--secondary-light` band、上 `--shadow-md`。`toggleFoodArea` 切 `.food-area.open` 並同步 `aria-expanded`。
- **清單 `.area-list`**（=原 `#food-XXX`）：展開才顯示，外包 `--secondary` 抽屜框。每家 `details.food-item` 仍可各自獨立展開；收合列含「名稱 + 類別 chip + 星等 + 招牌/價位預覽行」。
- **區尾 `.spot-walk-link`**：dashed 分隔 + 步行圖示 +「回景點漫遊 · {景點}散步路線」/「看步行距離・階梯・歇腳處與友善度」+ ↗，跳對應 `spot-XXX`。
- **視覺文法**：chevron＝原地展開、↗＝跳分頁，兩動作拆到區頭/區尾物理隔開，避免誤點。
- `jumpToFood(areaId)` 從景點跳來時**自動展開**目標區並定位。

### 6. 其餘
- 六區對照：`德壽宮/spot-deoksugung`、`景福宮・三清洞/spot-gyeongbok`、`仁寺洞/spot-insadong`、`首爾林/spot-seoulforest`、`聖水洞/spot-seongsu`、`首爾車站/spot-seoulstation`（首日緩衝 `spot-buffer` 無美食）。
- 保留：總覽景點畫廊、行前準備、通關 Stepper、機場接駁比較卡、免稅習俗、緊急一鍵撥號、類別 legend、導覽 active 自動置中。

---

## 設計決策摘要（為什麼這樣做）

- **美食「預覽行 + 標題展開」而非捲動方向自動開合**：後者造成版面跳動、方向判定拖影、奪使用者控制權；預覽行讓多數情況免展開即可掃讀，標題一鍵展開受控無跳動。
- **跳景點連結下放區尾、標題改展開**：原本把「跳走」綁在最重的標題、「原地展開」壓到邊角是主客顛倒且同列雙動作易誤點；翻轉後符合直覺。
- **暖色克制**：秋日暖色（楓紅/銀杏金）僅用於導引/分類/友善度，面積 ≤15%，大面積維持綠/白/米。

---

## 驗收基線（回歸測試時檢查）

- [ ] 長分頁捲到中段 → 切別分頁 → 回上頁，回到原分頁且原捲動高度；前進切換落在頂端。
- [ ] 左右滑動切分頁、且不吃掉導覽/chip/legend 的橫向捲動。
- [ ] 美食 6 區預設收合、點標題原地展開/收合、預覽收合態顯示、aria 同步；區尾連結跳對應景點；景點卡「本區美食 →」跳來自動展開。
- [ ] 30 家美食內容與連結未竄改；離線可開、無外連資源、無重複 id、localStorage try-catch、函式掛 window、結構控制項無 emoji。
