# `index.html` 前端功能增修計畫 (Feature Update Plan v3)

> 本計畫針對**已完成的 v2 重設計 `index.html`（現況 1960 行）**做兩組增量功能修改，非重寫。
> 事實來源仍為 `travel_韓國首爾_edited.md`（不得竄改任何價格/電話/連結/政策）；設計哲學仍遵循 `web_design_preference.md`（侘寂綠、行動核心一體化、540px 置中、單一 DOM、零外部依賴、可離線開啟）。
> 兩項使用者需求：**(A) 底部導覽 + 左右滑動 / 回上頁**、**(B) 美食分頁改為直接展開各景點食物並可回跳景點**。

---

## 0. 現況關鍵事實（實作前必讀）

- **Section 切換**：`switchSection(event, sectionId)`（`index.html:1848`），區段 id 順序為
  `overview · preparation · airport · spots · food · useful · emergency`（見 nav `index.html:496–520`）。
- **底部快捷列** `.bottom-bar`（`index.html:1829`）目前 3 顆：`緊急撥號` · `回總覽` · `回頂`。
- **美食內容目前放在「景點漫遊」各站卡片內**：每張 `.spot-card` 末尾有 `<h4 class="food-section-title">本區推薦美食</h4>` + `<div id="food-xxx">…5 家 details…</div>`。
- **「美食」分頁目前只是跳轉索引**（`index.html:1580–1631`）：6 顆 `.food-index-btn` 跳到景點漫遊的 `food-xxx` 錨點。
- 既有輔助函式：`scrollToAnchor(id)`（sticky 補償 96px）、`jumpToSpot(spotId)`、`jumpToFoodArea(id)`、`scrollToActiveNav()`。
- 既有橫向捲動容器（**滑動手勢必須避讓**）：`.nav-menu`（頂部導覽）、`.anchor-chip-row`（景點漫遊地名 chip）、`.food-index-legend`（美食類別 legend）、以及 `.food-actions` 等。

**六個美食區 ↔ 景點卡 ↔ 標題文案 對照（B 組會用到）：**

| 美食區 id | 對應景點卡 id | 標題（`景點: 美食概述`）|
|---|---|---|
| `deoksugung`  | `spot-deoksugung`  | 德壽宮: 味成屋・滿足五香豬腳・Liege Waffle 等 5 家 |
| `gyeongbok`   | `spot-gyeongbok`   | 景福宮・三清洞: 黃生家刀削麵・土俗村參雞湯 等 5 家 |
| `insadong`    | `spot-insadong`    | 仁寺洞: 開城餃子宮・仁寺洞蒜泥包肉 等 5 家 |
| `seoulforest` | `spot-seoulforest` | 首爾林: 奶奶的食譜・大成肋排 等 5 家 |
| `seongsu`     | `spot-seongsu`     | 聖水洞: 聖水一隻雞・大林倉庫 等 5 家 |
| `seoulstation`| `spot-seoulstation`| 首爾車站: 河東館・兔子停 等 5 家 |

> ⚠️ `首日緩衝 spot-buffer` 沒有美食清單，美食分頁維持 6 區。

---

## A. 底部導覽強化：回上頁 + 左右滑動切換分頁

**動機**：資訊量大、需交叉查閱（如在景點看到某站 → 跳去美食 → 想回原處）。

### A.1 底部快捷列新增「回上頁」（共 4 顆）

- `.bottom-bar` 改為 4 顆，順序：**`緊急撥號`（emphasis）· `回上頁` · `回總覽` · `回頂`**。
- 「回上頁」語意 = **回到「剛才看的那個分頁」（瀏覽歷史 back），非順序上的前一頁**（使用者已確認）。
- icon 沿用 inline SVG line-icon 風格（左箭頭 / 回轉箭頭，統一 20px、`stroke:currentColor`），**不得用 emoji**。
- 4 顆並排在 540px 容器與窄手機上：縮小 label 字級（如 11–12px）、icon 保持，觸控區仍 ≥44px 高；用 `flex:1` 均分、`min-width:0`、label 可換行或縮字避免爆版。
- 歷史堆疊為空時，「回上頁」為無作用（可視覺淡化 `opacity` 或直接 no-op，不跳錯頁）。

### A.2 瀏覽歷史堆疊（供「回上頁」）

在 `<script>` 內新增**記憶體內**歷史堆疊（不需持久化到 localStorage）：

- `let sectionHistory = [];`
- 改造 `switchSection(event, sectionId, opts)`，新增第三參數 `opts = { record = true }`：
  - 切換前取得目前 active section id；若 `record === true` 且 `目標 id !== 目前 id`，把**目前 id** `push` 進 `sectionHistory`（去重：與堆疊頂端相同就不 push；堆疊上限如 30 筆，超過捨最舊）。
  - 其餘切換邏輯（nav active、顯示 section、`scrollToActiveNav`、寫 `localStorage.activeSection`）維持不變。
- 新增 `goBack()`：
  - 若 `sectionHistory.length === 0` → no-op。
  - 否則 `const prev = sectionHistory.pop();` 然後 `switchSection(null, prev, { record: false })`（**back 導覽本身不再 push**，避免來回死循環）。
- **記得**：`window.goBack = goBack;`（行內事件全域掛載鐵則）。
- **初始化不 push**：`DOMContentLoaded` 內還原 `savedSection` 時呼叫 `switchSection(null, savedSection, { record: false })`。
- 既有會切分頁的呼叫端（nav 連結、`jumpToSpot`、總覽膠囊、緊急 CTA、A.3 滑動、B 組跳轉）維持 **record=true 預設**，讓「回上頁」能回到來源分頁。

### A.3 左右滑動切換分頁（touch swipe）

- 在 `.app-container`（或 `document`）掛 `touchstart` / `touchend`：記錄起點 `x,y`、終點 `x,y`。
- **判定為有效水平滑動**需同時滿足：`|dx| > 60px`、且 `|dx| > 2 * |dy|`（避免與垂直捲動打架）。
- **避讓橫向捲動容器（重要，防手勢衝突，呼應 §1.11 / §3.3）**：`touchstart` 時，若起點 `e.target.closest()` 命中任一可橫向捲動容器（`.nav-menu, .anchor-chip-row, .food-index-legend, .food-actions`），或往上尋找到任一 `overflow-x` 為 `auto/scroll` 且 `scrollWidth > clientWidth` 的祖先，則**本次滑動忽略**（讓該容器自行橫滑）。
- 方向 → 分頁：以 `SECTION_ORDER = ['overview','preparation','airport','spots','food','useful','emergency']` 為序。
  - **左滑（dx < 0，手指由右往左）→ 下一分頁**；**右滑（dx > 0）→ 上一分頁**。
  - 到頭 / 到尾則不動（不循環）。
  - 切換走 `switchSection(null, nextId)`（**record=true**，讓「回上頁」也能回溯滑動來源）。
- 純 touch 即可（桌面用按鈕/導覽），不加滑鼠拖曳，維持 JS 極簡。
- `window` 掛載新函式（如 `window.goBack`）；swipe 監聽在 init 內註冊（如 `setupSwipeNavigation()`）。

---

## B. 美食分頁改為「直接展開各景點食物」+ 標題可回跳景點

**使用者確認的唯一來源方案：把美食內容「移到美食分頁」，景點卡改放跳轉連結**（避免重複、避免 id 衝突）。

### B.1 內容搬移（單一來源）

1. **從每張 `.spot-card` 移除**其 `<h4 class="food-section-title">本區推薦美食</h4>` 與其後的 `<div id="food-xxx">…</div>` 整塊（6 站：deoksugung / gyeongbok / insadong / seoulforest / seongsu / seoulstation）。
2. 在景點卡原位置，改放一顆精簡跳轉列 **`本區美食 →`**（新 class `.food-jump-link`，含餐具 line-icon），`onclick="jumpToFood('deoksugung')"` 之類，跳到美食分頁對應區。
3. **「美食」分頁**：刪除現有 6 顆 `.food-index-btn`（`index.html:1595–1630`），改為 6 個**直接展開的美食區塊**，每區結構：
   ```html
   <div class="food-area" id="food-area-deoksugung">
     <button class="food-area-title" onclick="jumpToSpot('spot-deoksugung')">
       <span>德壽宮: 味成屋・滿足五香豬腳・Liege Waffle 等 5 家</span>
       <svg class="jump-arrow" viewBox="0 0 24 24">…（↗ 斜向箭頭，表示可跳轉）…</svg>
     </button>
     <div id="food-deoksugung">
       …原封搬過來的 5 家 <details class="food-item"> …
     </div>
   </div>
   ```
   - **`food-item` details 內容完全照搬、不改字不改連結**（價位/招牌/食記/Naver/Kakao 一字不動）。
   - 保留原 `id="food-xxx"` 於內層 div 無妨；跳轉錨點用外層 `food-area-xxx`。
4. 保留美食分頁頂端的**類別 legend**（`.food-index-legend`：正餐/小吃/咖啡廳/伴手禮 chip）作為顏色對照。

### B.2 標題格式與文字導引

- **標題格式**：`景點名稱: 美食概述`（見 §0 對照表），如「德壽宮: 味成屋・滿足五香豬腳・Liege Waffle 等 5 家」。
- **標題可點擊 → 跳到該景點漫遊區塊**（`jumpToSpot('spot-xxx')`）。視覺上要看得出可點：主色字/底線或 hover 態 + 尾端 `↗` 斜箭頭 icon（沿用 line-icon，非 emoji）。觸控區 ≥44px 高。
- **簡短導引文案**：把美食分頁頂端 `.section-sub`（`index.html:1586`）文字改為明確引導，例如：
  > 「各區美食已直接展開，點**區塊標題**即可跳到「景點漫遊」對應景點看詳細散步路線。」
  （一句即可，避免每區重複囉嗦；標題本身的 `↗` 已提供可點暗示。）

### B.3 JS 調整

- **新增** `jumpToFood(areaId)`：`switchSection(null, 'food'); scrollToAnchor('food-area-' + areaId);`（record=true → 之後可「回上頁」回景點漫遊）。掛 `window.jumpToFood`。
- **`jumpToSpot(spotId)`** 沿用（美食分頁標題點擊 → 跳景點）；確認它切到 `spots` 亦走 record=true。
- **移除** 已無用的舊 `jumpToFoodArea`（原本 spots→food 錨點索引邏輯），或改寫為 `jumpToFood`。清掉對應 `window.jumpToFoodArea`。
- CSS：`.food-index-group` / `.food-index-btn` 若不再使用可刪；新增 `.food-area` / `.food-area-title` / `.food-jump-link` 樣式（低飽和、和諧於侘寂綠 + 秋日暖，遵循既有 token；標題用 `--text-main`/`--primary`，箭頭用 `--primary`）。

---

## C. 不得破壞的鐵則（每次改動都自檢）

- **單一 DOM、零外部依賴、可離線開啟**：不得新增任何外連字型/CDN/圖片/API；新 icon 一律 inline SVG。
- **`localStorage` 全包 `try...catch`**；歷史堆疊為記憶體內即可，不影響此鐵則。
- **所有行內 `onclick` 函式顯式掛 `window`**（`goBack`、`jumpToFood` 等新函式務必掛載）。
- **結構控制項（底部按鈕、標題、chip、箭頭）嚴禁 emoji**，一律 line-icon。
- 事實（價格/限重/電話/政策/日期/連結）與 `travel_韓國首爾_edited.md` 一致，**搬移不改字**。
- 滑動不得吃掉頂部導覽、地名 chip、類別 legend 的橫向捲動（§A.3 避讓）。

---

## D. 驗收檢核表

**A 組**
- [ ] 底部 4 顆：緊急撥號 / 回上頁 / 回總覽 / 回頂，窄手機不爆版、觸控區 ≥44px、無 emoji。
- [ ] 「回上頁」回到**上一個瀏覽的分頁**（歷史 back），空堆疊時 no-op、不跳錯頁、不死循環。
- [ ] 左滑→下一分頁、右滑→上一分頁；到頭/尾不動、不循環。
- [ ] 滑動避讓所有橫向捲動容器（導覽 / 地名 chip / 類別 legend 仍可正常橫滑）。
- [ ] nav 點擊 / 跳轉 / 滑動皆能被「回上頁」正確回溯；初始化還原不誤記歷史。

**B 組**
- [ ] 美食分頁**直接展開** 6 區、每區 5 家 details（內容一字未改）。
- [ ] 每區標題為「景點: 美食概述」格式，可點跳到對應景點卡（`↗` 明示可點）。
- [ ] 美食分頁頂端有簡短導引文案；類別 legend 保留。
- [ ] 景點卡的美食清單已移除，改為「本區美食 →」跳轉列，跳到美食分頁對應區。
- [ ] 全站無 `food-xxx` id 重複；舊 `jumpToFoodArea` 已清理。

**C 鐵則**
- [ ] 離線可開（無外連資源）；localStorage 有 try-catch；新函式全掛 `window`；結構控制項無 emoji。

---

## E. 執行順序（交派 sonnet）

1. **先 commit 現況檢查點**：檢視 `git diff` / `git status`，將目前 travel_guide 專案有意義的變更（`index.html` v2 重設計、`plan.md`、`.gitignore`）提交為一個檢查點 commit；`.claude/`、`.agents/` 等本機工作目錄依 `.gitignore` 判斷是否納入（不確定就不強加）。
2. **再依本計畫實作 A、B 兩組**（建議先 A.2 歷史堆疊改造 → A.1 按鈕 → A.3 滑動 → B 搬移與跳轉），逐項對照 §D 自檢。
3. 實作完成後，開瀏覽器/本機驗證行為（分頁切換、回上頁、左右滑動、美食展開與雙向跳轉、離線資源檢查），再提交實作 commit。

---

## F. （v3.1 追加）美食清單降低點擊摩擦：預覽行 + 展開全部

**動機**：美食分頁 6 區 × 5 家 = 30 個 `<details>` 全收合，要看得點很多次。使用者提議「依捷動方向自動展開/收合」，但那會造成版面跳動、方向判定拖影、奪控制權（已討論否決）。**定案方案：讓大多數情況根本不用展開（預覽行）+ 想全看時一鍵搬定（展開全部）**。零捷動監聽、無版面拖影、受控。

### F.1 收合列新增「預覽行」（30 家）

- 在每個 `<summary class="food-item-summary">` 內，**新增第三個子元素**（現有兩個：名稱組 / 星等+箭頭組 維持不動）：
  ```html
  <span class="food-preview">招牌 {該家招牌菜原文}・{該家價位帶原文}</span>
  ```
- **內容一律直接搬用該 details body 內的「招牌菜」與「價位帶」原文，一字不改、不重寫、不新編任何數字**（避免截短變造事實）。中間以「・」隔開；前置一個小標「招牌」。
  例：味成屋 → `招牌 韓牛雪濃湯 (설렁탕)・雪濃湯小份 11k 韓元，大份 13k 韓元；白切牛肉盤大份 45k 韓元。`
- 過長一律以 CSS **單行省略號截斷**（`white-space:nowrap; overflow:hidden; text-overflow:ellipsis`），不手動削字。
- **展開後隱藏預覽行**（body 已有完整招牌菜/價位帶，避免重複）：`.food-item[open] .food-preview { display:none; }`。

**CSS**：
- `.food-item-summary` 新增 `flex-wrap: wrap;`（讓預覽行換到第二行滿寬）。
- 新增 `.food-preview { flex-basis:100%; width:100%; font-size:13px; color:var(--text-muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:2px; }`（「招牌」小標可用 `var(--ginkgo)` 稍作區隳，但不強制）。

### F.2 每區新增「展開全部 / 收合全部」（6 區）

- 在每個 `.food-area` 內、`.food-area-title` 之後、`#food-xxx` 之前，插入一列工具列（右對齊）：
  ```html
  <div class="food-area-toolbar">
    <button class="food-expand-all" onclick="toggleFoodArea(this)" aria-label="展開或收合本區全部美食">
      <span>展開全部</span>
      <svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg>
    </button>
  </div>
  ```
- **JS `toggleFoodArea(btn)`**（自校正、偵測現況）：
  ```js
  function toggleFoodArea(btn){
    const area = btn.closest('.food-area');
    if(!area) return;
    const items = area.querySelectorAll('details.food-item');
    const anyClosed = Array.from(items).some(d => !d.open); // 有任何一家收著 → 本次全開
    items.forEach(d => { d.open = anyClosed; });
    btn.classList.toggle('open', anyClosed);          // open 態 → 箭頭朝上
    btn.querySelector('span').textContent = anyClosed ? '收合全部' : '展開全部';
  }
  window.toggleFoodArea = toggleFoodArea; // 行內事件必須全域掛載
  ```
  - 這個「有任何收著→全開；全開→全收」邏輯對使用者手動開關個別項目後仍能自行修正，不會卡死。
  - `food-item` 本就無 `name` 屬性（非互斥），可全部同時展開；也不受既有 `setupExclusiveAccordions`（只管 `details[name]`）影響。

**CSS**：
- `.food-area-toolbar { display:flex; justify-content:flex-end; margin:-4px 0 10px; }`
- `.food-expand-all { display:inline-flex; align-items:center; gap:6px; background:var(--secondary-light); color:var(--primary-hover); border:none; border-radius:8px; padding:8px 12px; font-size:13px; font-weight:700; cursor:pointer; font-family:inherit; min-height:40px; }`
- `.food-expand-all svg { width:16px; height:16px; fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; transition:transform .25s ease; }`
- `.food-expand-all.open svg { transform:rotate(180deg); }`

### F.3 驗收（串入 §D）

- [ ] 30 家收合列都有預覽行，內容＝該家「招牌菜 + 價位帶」**原文連接**（預覽行出現的每一個數字/文字都能在該 details body 找到，無新編事實）；展開後預覽行隱藏。
- [ ] 6 區各有一顆展開/收合切換鈕；點一下全區開、再點全區收，標題與箭頭隨狀態更新；toggleFoodArea 已掛 `window`。
- [ ] 無 emoji（箭頭皆 inline SVG）；離線可開、localStorage 仍 try-catch——這些鐵則未被破壞。
- [ ] 預覽行不會擐爆 summary 版面（兩行式：第一行 名稱/星等，第二行 滿寬預覽並省略號截斷）。
