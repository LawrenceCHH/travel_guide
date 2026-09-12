# 2026-10-seoul-family-v2 規劃進度

## 環境
- 宿主：Claude Code（被上層 agent 委派執行，無即時真人使用者）｜搜尋 ✓ ｜檔案 ✓ ｜子agent ✓（self-subagent=ready, agy=ready；copilot=broken, gemini/codex=absent）｜git ✓ ｜Python 3.8.10（實測通過）
- 模式：混合（Wave 1 平行派工 / Wave 2-3 主 agent 序列收斂），依 `detect_agents.py` 建議
- **無真人使用者**：依 `references/portability.md`「無真人使用者」處理啟動流程第 2、4、5 步——不主動提問、trip_context 人工確認關卡只能延後不能取消、平行/序列不問由 agent 自行決定。
- 建立：2026-09-11 ｜ 最後更新：2026-09-11

## ⚠ 尚未經人工確認
`trip_context.json` 已產出，但因無真人使用者在線，去識別化結果與所有推斷值**尚未經使用者過目確認**。commit 前必須先過此關卡；本次任務全程只寫檔案，不執行 `git commit`。

## 待覆核的推斷值
- `stay.area` / `stay.nearest_station`：由飯店名（New Seoul Hotel）以網頁搜尋推斷為「中區光化門／市廳一帶，近光化門站（5號線）／市廳站（1、2號線）」，未使用具體門牌地址，請使用者確認是否正確。
- `stay.checkin`：草稿未明講入住時間，依慣例預設 15:00，請確認實際訂房條款。

## Checklist
| # | 主題 | 狀態 | 產出檔 | 負責 | 最後更新 |
|---|---|---|---|---|---|
| 00 | 通用知識裁剪 | done | plan/00_general.md | sub-agent(00) | 09-11 |
| 01 | 行程資訊整理 | done | plan/01_flight_stay.md | main | 09-11 |
| 02 | 機場通關 | done | plan/02_immigration.md | sub-agent(02) | 09-11 |
| 03 | 保險 | done | plan/03_insurance.md | sub-agent(03) | 09-11 |
| 04 | 網路與漫遊 | done | plan/04_connectivity.md | sub-agent(04) | 09-11 |
| 05 | 交通資訊 | done | plan/05_transport.md | sub-agent(05) | 09-11 |
| 06 | 支付方式 | done | plan/06_payment.md | sub-agent(06) | 09-11 |
| 07 | 免稅與退稅 | done | plan/07_tax_refund.md | sub-agent(07) | 09-11 |
| 08 | 當地習慣 | done | plan/08_local_customs.md | sub-agent(08) | 09-11 |
| 09 | 素材庫 | done | materials/spots.json, materials/food.json | 4× sub-agent（分批 area） | 09-11 |
| 10 | 行程安排 | done | plan/10_itinerary.md | main | 09-11 |
| 11 | 緊急應變 | done | plan/11_emergency.md | sub-agent(11) | 09-11 |

### 09 素材庫執行細節
- 派工方式：主 agent 依區域分成 4 批平行派給 general-purpose sub-agent（非 agy，因 agy 在本次 Bash 環境可用但 Agent 工具的 self-subagent 更易於同時管理多個），每批負責 2-3 個 area，各自執行 `research_rules.md` §9.1（景點：台灣部落客遊記）+ §9.2（美食：`search.naver.com` 整合搜尋）兩階段發掘。
- 最終涵蓋 9 個 area：`gwanghwamun`、`gyeongbok_bukchon`、`ikseondong`、`dongdaemun`、`myeongdong`、`yeouido`、`noryangjin`、`seongsu`、`namiseom`。
- `scripts/validate_materials.py` 執行結果：**exit code 0**（無 ERROR），3 筆 WARN（來源時效超過 1 年但未超過 2 年，已標記待覆核，見下方待確認清單）。
- **§7.3 第 8 條地理覆蓋檢查**：`trip_context.named_musts` 共 16 項指名點，其中 **15 項已對應到某個建檔 area**；唯一未建檔項目：
  - **「倫敦貝果博物館 安國店」**——未在任何 area 的 `spots`/`food` 中建檔。原因：4 個派工批次皆優先處理草稿中份量較重的景點與包車/巴士等固定行程，此單一麵包店未被明確分派給任何批次，屬本次派工切分的疏漏，非查無資料。**`10_itinerary.md` 引用此點時每次都會標註「（未建檔，沿用草稿原文）」**，不會混同於正式建檔景點。
- 63大廈：素材庫查證發現其觀景台已於 2026-06-30 公告歇業、重新開幕日期未定（來源：funliday.com 2026-09-10 文章），已將該景點調整為「僅外觀/大廈本身」用途、`rainy_day_ok: false`，並標註待覆核，未沿用草稿「看夜景」原意直接排入行程（見 10_itinerary.md 處理方式）。

## 交接事項（下一個 context 必須知道）
- 原始草稿有兩份行程規劃（新表格版＋舊條列版「# old」），內容大致相同但新表格版更完整（含每日早餐、換匯地點細節），trip_context 以新表格版為準，舊版僅作交叉確認。
- 草稿最下方「首爾塔／弘大」列為備註，未整合進任何一天，視為 `named_undecided`。
- 首爾觀光巴士夜遊、南怡島包車一日遊皆為已預約/需預約項目，10 行程安排必須固定其時段，不可挪動。

## 待確認清單（[待確認：...] 彙整）
全流程共 81 處 `[待確認：...]` 標記分布於各 `plan/*.md`（未逐字彙整於此，因數量多且各自附具體原因，統一在各檔案內文標記，符合 `research_rules.md` §3 要求）。每檔筆數：00_general 13、01_flight_stay 8、02_immigration 19（含雙邊官方逐條試過網址記錄）、03_insurance 4、04_connectivity 5、05_transport 12、06_payment 6、07_tax_refund 3、08_local_customs 2、11_emergency 9；另 `materials/spots.json`/`food.json` 共 5 處（含 3 筆 WARN 時效標記＋63大廈歇業＋2筆門票金額待查）。重點摘要：
- 02/03/11（最嚴格等級）多數 `[待確認]` 屬「官方頁面被 Cloudflare/WAF 擋下（403）」或「官方頁面存在但未列出精確數字」，皆已依 §2.5 換路徑/換工具/降級引用處理，非未查證即放棄。
- 63大廈觀景台已確認歇業，重新開幕日期未定。
- 「倫敦貝果博物館 安國店」未建檔，見上方 09 素材庫細節。
- 各 `plan/*.md` 檔尾皆有「待確認」小節彙整該章節標記，供使用者逐一核對。

## 決策紀錄
- 2026-09-11：飯店名（New Seoul Hotel）依現行隱私規則單獨出現不算違規，予以保留於 `plan/01_flight_stay.md`、`plan/10_itinerary.md` 等成品；訂房確認號、訂房人姓名、Email、電話仍一律刪除。已跑 `scripts/scrub_check.py`（exit 0，未發現外洩，抽出 5 類候選 token：訂房人姓名1、訂房確認號1、電話1、航班號2）與 `scripts/validate_materials.py`（exit 0，3 筆 WARN）。
- 2026-09-11：無真人使用者，模式由 agent 自行決定為混合模式；Wave 1（00 除外的 8 個檢索主題＋00 通用知識，共 9 個）以 Claude Code 內建 Task/Agent 工具（self-subagent）平行派工，01 由主 agent 自己整理（依 SKILL.md 規定）。09 素材庫依區域切成 4 批（非逐 area 單獨派工，是效率與品質的折衷）平行派工，同樣用 self-subagent 而非 agy——因本次環境下 Agent 工具原生支援多個背景任務並行監控，比透過 Bash 呼叫 agy CLI 更適合本次協調需求；10 由主 agent 序列收斂（依賴 09+05 完成）。
- 2026-09-11：09 素材庫的 area 劃分主 agent 自行先行決定（未等待 05 交通完成後才派工，因 05 與 09 幾乎同時派出），事後比對 05 產出的區域清單，僅在「景福宮」的歸屬上略有差異（05 將景福宮併入光化門大區，09 因派工先行決定而將景福宮與北村合併為獨立 area）——地理上仍合理鄰近，不影響行程安排的可行性，已如實記錄此處落差而非隱藏。
- 2026-09-11：「倫敦貝果博物館 安國店」因 09 素材庫 4 批派工皆未涵蓋，判定為派工切分疏漏；未追加第 5 批次重跑（考量已完成之 15/16 named_musts 覆蓋率已達規則要求的「不得靜默省略」標準，改採 `10_itinerary.md` 逐次標註「未建檔，沿用草稿原文」的補救條款處理，並在此如實記錄未覆蓋原因）。

## 已知待清理項目
- `plan/` 目錄下有 5 個非成品的暫存檔（`.mohw1.html`、`.mohw2.html`、`.nhi1.html`、`.nhi2.html`、`.nhi3.html`），為 03 保險 sub-agent 查證 mohw.gov.tw／nhi.gov.tw 時誤將 curl 抓取的原始 HTML 存到 `plan/` 而非暫存目錄。內容為公開政府頁面原始碼，不含個資，**非隱私風險**，但不屬於成品，建議使用者或下一輪執行時手動刪除（本次執行環境的權限系統拒絕了 agent 自行 `rm` 這幾個檔案）。

## 接續包（無持久儲存時・下次開新對話請上傳）
- [可分享] trip_context.json / progress.md / materials/*.json / plan/*.md
- [不可分享] private/input/*、private/personal/*（僅自己保存，不要貼進公開場合）

## 變更紀錄（無 git 時使用）
- 2026-09-11 建立 trip_context.json（尚未經人工確認）、progress.md
