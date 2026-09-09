<!--
建立新旅程時複製本檔為 trips/{trip}/progress.md 並填入。
完整格式說明與更新時機見 references/progress_protocol.md。
-->

# {trip} 規劃進度

## 環境
- 宿主：{Claude Code / claude.ai 網頁版 / ...} ｜搜尋 {✓/✗} ｜檔案 {✓/✗} ｜子agent {✓/✗} ｜git {✓/✗} ｜Python {版本或「未偵測到」}
- 模式：{序列 / 平行 / 混合}
- 建立：{YYYY-MM-DD} ｜ 最後更新：{YYYY-MM-DD}

## 待覆核的推斷值
- （由 trip_context.json 的 inferred_fields 帶入，逐項列出並說明推斷依據）

## Checklist
| # | 主題 | 狀態 | 產出檔 | 負責 | 最後更新 |
|---|---|---|---|---|---|
| 00 | 通用知識裁剪 | pending | plan/00_general.md | — | — |
| 01 | 行程資訊整理 | pending | plan/01_flight_stay.md | — | — |
| 02 | 機場通關 | pending | plan/02_immigration.md | — | — |
| 03 | 保險 | pending | plan/03_insurance.md | — | — |
| 04 | 網路與漫遊 | pending | plan/04_connectivity.md | — | — |
| 05 | 交通資訊 | pending | plan/05_transport.md | — | — |
| 06 | 支付方式 | pending | plan/06_payment.md | — | — |
| 07 | 免稅與退稅 | pending | plan/07_tax_refund.md | — | — |
| 08 | 當地習慣 | pending | plan/08_local_customs.md | — | — |
| 09 | 素材庫 | pending（等 05） | materials/spots.json, materials/food.json | — | — |
| 10 | 行程安排 | pending（等 09） | plan/10_itinerary.md | — | — |
| 11 | 緊急應變 | pending | plan/11_emergency.md | — | — |

## 交接事項（下一個 context 必須知道）
- （初始為空，每階段結束時補上下個 context 需要的重點）

## 待確認清單（[待確認：...] 彙整）
- （初始為空）

## 決策紀錄
- （初始為空，記錄偏離預設規則的判斷與理由）

## 接續包（無持久儲存時・下次開新對話請上傳）
- [可分享] trip_context.json / progress.md / materials/*.json / plan/*.md
- [不可分享] private/input/*、private/personal/*（僅自己保存，不要貼進公開場合）

## 變更紀錄（無 git 時使用）
- （初始為空，無 git 環境每次更新時新增一行 `YYYY-MM-DD HH:MM 摘要`）
