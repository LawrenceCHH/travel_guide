#!/usr/bin/env python3
"""validate_materials.py — 校驗 spots.json / food.json 是否符合硬約束。

依據 references/sections/09_materials.md §7.3 的七條硬約束執行機械校驗：
  1. 每個 area 的 food.picks 必須含觀光客 3 家 + 當地人 3 家，且 category 橫跨至少 3 類。
  2. 跨日反重複：同一主食類型（依 signature 判斷）全書最多出現 2 次。
  3. 每筆（spots/food）必須有非空 sources，且 url 去掉 domain 後路徑不可為空。
  4. sources.published 距今超過 1 年標記 WARN，超過 2 年判 ERROR。
  5. 每個 area 至少 1 個 rainy_day_ok: true 的景點（供 Plan B）。
  6. food.near_spot 必須存在於 spots.json 的同一 area 中（參照完整性）。
  7. 所有列舉欄位的值必須落在合法值清單內。

只使用 Python 3 標準庫，不 import 任何第三方套件。
只做校驗，不做檢索與判斷；失敗時輸出非零 exit code 與可讀的違規清單（區分 ERROR / WARN）。

用法：
    python3 validate_materials.py --spots materials/spots.json --food materials/food.json
    python3 validate_materials.py --spots materials/spots.json --food materials/food.json --today 2026-09-09

Exit code：
    0 = 無 ERROR（可能仍有 WARN）
    1 = 至少一項 ERROR
    2 = 執行本身失敗（檔案不存在、JSON 格式錯誤等）
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from urllib.parse import urlparse

SPOT_CATEGORIES = {"文化古蹟", "自然景觀", "購物商圈", "網美打卡", "體驗活動", "室內歇腳"}
SPOT_AUDIENCES = {"tourist_must", "local_favorite"}
FOOD_CATEGORIES = {"正餐", "小吃", "咖啡甜點", "伴手禮"}
FOOD_AUDIENCES = {"tourist", "local"}
SOURCE_TIERS = {"official", "platform", "blogger"}

MIN_TOURIST_PICKS = 3
MIN_LOCAL_PICKS = 3
MIN_CATEGORY_SPAN = 3
MAX_SAME_STAPLE = 2
WARN_AFTER_DAYS = 365
ERROR_AFTER_DAYS = 365 * 2


class Report:
    def __init__(self):
        self.errors = []
        self.warns = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def ok(self):
        return not self.errors

    def print_all(self):
        if self.errors:
            print(f"=== ERROR（{len(self.errors)}） ===")
            for m in self.errors:
                print(f"  [ERROR] {m}")
        if self.warns:
            print(f"=== WARN（{len(self.warns)}） ===")
            for m in self.warns:
                print(f"  [WARN]  {m}")
        if not self.errors and not self.warns:
            print("全數通過，無 ERROR 或 WARN。")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def url_has_deep_path(url):
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    path = (parsed.path or "").strip("/")
    return bool(path)


def check_source(source, ctx, today, report):
    for field in ("title", "site", "url", "published", "tier"):
        if not source.get(field):
            report.error(f"{ctx}：sources 物件缺少必填欄位 '{field}'")
    url = source.get("url", "")
    if url and not url_has_deep_path(url):
        report.error(f"{ctx}：url 去掉 domain 後路徑為空 -> {url}")
    tier = source.get("tier")
    if tier and tier not in SOURCE_TIERS:
        report.error(f"{ctx}：tier 值 '{tier}' 不在合法清單 {sorted(SOURCE_TIERS)}")
    published = source.get("published")
    if published:
        try:
            pub_date = datetime.strptime(published, "%Y-%m-%d").date()
            age_days = (today - pub_date).days
            if age_days > ERROR_AFTER_DAYS:
                report.error(f"{ctx}：published={published} 距今超過 2 年，判不合格")
            elif age_days > WARN_AFTER_DAYS:
                report.warn(f"{ctx}：published={published} 距今超過 1 年，需標記待覆核")
        except ValueError:
            report.error(f"{ctx}：published='{published}' 非合法日期格式（需 YYYY-MM-DD）")


def validate_spots(spots_data, report):
    """回傳 (spot_ids_by_area, rainy_day_by_area)"""
    spot_ids_by_area = {}
    rainy_day_by_area = {}

    areas = spots_data.get("areas", [])
    if not areas:
        report.error("spots.json：areas 為空")

    all_area_ids = {area.get("id", "<未命名>") for area in areas}

    for area in areas:
        area_id = area.get("id", "<未命名>")
        spot_ids = {spot.get("id", "<未命名>") for spot in area.get("spots", [])}
        has_rainy = False

        for nearby in area.get("nearby_areas") or []:
            ref = nearby.get("area_id")
            if ref and ref not in all_area_ids:
                report.error(f"area '{area_id}'.nearby_areas：area_id='{ref}' 不存在（參照完整性，規則 9）")

        for spot in area.get("spots", []):
            spot_id = spot.get("id", "<未命名>")
            ctx = f"spots.{area_id}.{spot_id}"

            for nearby in spot.get("nearby_spots") or []:
                ref = nearby.get("id")
                if ref and ref not in spot_ids:
                    report.error(f"{ctx}.nearby_spots：id='{ref}' 在同一 area 內找不到（參照完整性，規則 9）")

            category = spot.get("category")
            if category and category not in SPOT_CATEGORIES:
                report.error(f"{ctx}：category 值 '{category}' 不在合法清單 {sorted(SPOT_CATEGORIES)}")

            audiences = spot.get("audience", [])
            for aud in audiences:
                if aud not in SPOT_AUDIENCES:
                    report.error(f"{ctx}：audience 值 '{aud}' 不在合法清單 {sorted(SPOT_AUDIENCES)}")

            if spot.get("rainy_day_ok") is True:
                has_rainy = True

            sources = spot.get("sources") or []
            if not sources:
                report.error(f"{ctx}：sources 為空")
            for i, source in enumerate(sources):
                check_source(source, f"{ctx}.sources[{i}]", VALIDATE_TODAY, report)

        spot_ids_by_area[area_id] = spot_ids
        rainy_day_by_area[area_id] = has_rainy
        if not has_rainy:
            report.error(f"area '{area_id}'：沒有任何 rainy_day_ok=true 的景點（違反規則 5）")

    return spot_ids_by_area


# 常見修飾語：出現在招牌菜名裡但不改變主食類型，比對前先剝掉。
# 例：「元祖人蔘雞湯」與「蔘雞湯」應視為同一種。
STAPLE_MODIFIERS = (
    "元祖", "本家", "老字號", "傳統", "手工", "特製", "招牌", "限定", "名物",
    "人", "韓式", "韓國", "首爾", "宮廷", "土種", "生", "炭火", "石鍋",
)


def normalize_staple(text):
    """把招牌菜名正規化成可比對的字串：去空白、去標點、剝掉不影響主食類型的修飾語。"""
    text = re.sub(r"[\s\-_·・（）()\[\]【】、,，.。/／]+", "", (text or "").strip())
    for m in STAPLE_MODIFIERS:
        text = text.replace(m, "")
    return text


def guess_staple(name, signature):
    """判斷「主食類型」：優先用 signature，否則用店名，回傳正規化後的比對字串。"""
    return normalize_staple(signature or name or "")


def group_staples(all_staples):
    """把主食類型分組：正規化後互為包含關係（且長度 >= 2）者視為同一種。

    完全字串比對會讓規則 2 形同虛設——招牌菜名差一個字（「蔘雞湯」vs「人蔘雞湯」）
    就會被當成兩種，全書出現五次也抓不到。改用包含比對涵蓋這類同義寫法。
    """
    groups = []  # [(代表字串, [occurrence, ...])]
    for staple, area_id, pick_id in all_staples:
        if len(staple) < 2:
            continue
        occurrence = f"{area_id}.{pick_id}"
        for group in groups:
            rep = group[0]
            if staple == rep or staple in rep or rep in staple:
                # 以較短者當代表，代表的是共同的主食核心字
                if len(staple) < len(rep):
                    group[0] = staple
                group[1].append(occurrence)
                break
        else:
            groups.append([staple, [occurrence]])
    return groups


def validate_food(food_data, spot_ids_by_area, report):
    areas = food_data.get("areas", [])
    if not areas:
        report.error("food.json：areas 為空")

    all_staples = []  # (staple_text, area_id, pick_id)

    for area in areas:
        area_id = area.get("id", "<未命名>")
        tourist_count = 0
        local_count = 0
        categories_seen = set()
        known_spot_ids = spot_ids_by_area.get(area_id)

        if known_spot_ids is None:
            report.warn(f"food area '{area_id}'：在 spots.json 中找不到對應的 area，無法檢查 near_spot 參照完整性")

        for pick in area.get("picks", []):
            pick_id = pick.get("id", "<未命名>")
            ctx = f"food.{area_id}.{pick_id}"

            category = pick.get("category")
            if category and category not in FOOD_CATEGORIES:
                report.error(f"{ctx}：category 值 '{category}' 不在合法清單 {sorted(FOOD_CATEGORIES)}")
            else:
                categories_seen.add(category)

            audience = pick.get("audience")
            if audience and audience not in FOOD_AUDIENCES:
                report.error(f"{ctx}：audience 值 '{audience}' 不在合法清單 {sorted(FOOD_AUDIENCES)}")
            elif audience == "tourist":
                tourist_count += 1
            elif audience == "local":
                local_count += 1

            near_spot = pick.get("near_spot")
            if near_spot:
                if known_spot_ids is not None and near_spot not in known_spot_ids:
                    report.error(f"{ctx}：near_spot='{near_spot}' 在 spots.json 的 area '{area_id}' 中找不到（參照完整性違反，規則 6）")
            else:
                report.error(f"{ctx}：缺少 near_spot")

            sources = pick.get("sources") or []
            if not sources:
                report.error(f"{ctx}：sources 為空")
            for i, source in enumerate(sources):
                check_source(source, f"{ctx}.sources[{i}]", VALIDATE_TODAY, report)

            if category == "正餐" or category == "小吃":
                all_staples.append((guess_staple(pick.get("name", ""), pick.get("signature")), area_id, pick_id))

        if tourist_count < MIN_TOURIST_PICKS:
            report.error(f"area '{area_id}'：觀光客(tourist) picks 只有 {tourist_count} 家，需至少 {MIN_TOURIST_PICKS} 家")
        if local_count < MIN_LOCAL_PICKS:
            report.error(f"area '{area_id}'：當地人(local) picks 只有 {local_count} 家，需至少 {MIN_LOCAL_PICKS} 家")
        if len(categories_seen) < MIN_CATEGORY_SPAN:
            report.error(f"area '{area_id}'：category 只橫跨 {len(categories_seen)} 類（{sorted(categories_seen)}），需至少 {MIN_CATEGORY_SPAN} 類")

    # 跨日反重複：同一主食類型全書最多出現 2 次（包含比對，見 group_staples）
    for staple, occurrences in group_staples(all_staples):
        if len(occurrences) > MAX_SAME_STAPLE:
            report.error(
                f"主食類型 '{staple}' 全書出現 {len(occurrences)} 次（{', '.join(occurrences)}），"
                f"超過上限 {MAX_SAME_STAPLE} 次（規則 2）"
            )


VALIDATE_TODAY = date.today()


def main():
    global VALIDATE_TODAY
    parser = argparse.ArgumentParser(
        description="校驗 spots.json / food.json 是否符合 09_materials.md §7.3 的七條硬約束。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--spots", required=True, help="spots.json 路徑")
    parser.add_argument("--food", required=True, help="food.json 路徑")
    parser.add_argument("--today", default=None, help="校驗基準日期 YYYY-MM-DD（預設為系統今天，測試用）")
    args = parser.parse_args()

    if args.today:
        try:
            VALIDATE_TODAY = datetime.strptime(args.today, "%Y-%m-%d").date()
        except ValueError:
            print(f"--today 格式錯誤：{args.today}，需 YYYY-MM-DD", file=sys.stderr)
            sys.exit(2)

    try:
        spots_data = load_json(args.spots)
    except (OSError, json.JSONDecodeError) as e:
        print(f"讀取/解析 {args.spots} 失敗：{e}", file=sys.stderr)
        sys.exit(2)

    try:
        food_data = load_json(args.food)
    except (OSError, json.JSONDecodeError) as e:
        print(f"讀取/解析 {args.food} 失敗：{e}", file=sys.stderr)
        sys.exit(2)

    report = Report()
    spot_ids_by_area = validate_spots(spots_data, report)
    validate_food(food_data, spot_ids_by_area, report)

    report.print_all()

    if not report.ok():
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
