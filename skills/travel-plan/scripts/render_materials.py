#!/usr/bin/env python3
"""render_materials.py — 把 spots.json / food.json 轉成人可讀的 md 表格，並可正規化 JSON 本身。

強制執行 references/sections/09_materials.md §7.2 的輸出約定：
  - 欄位順序固定（依 schema 宣告順序輸出，不因重新產生而重排）
  - 巢狀不超過 3 層（root -> areas -> spots/picks -> 物件欄位）
  - sources 陣列每個來源物件寫成一行
  - 縮排 2 空格，UTF-8，不轉義非 ASCII（ensure_ascii=False）
  - 檔尾保留換行

只使用 Python 3 標準庫，不 import 任何第三方套件。
只做格式轉換，不做檢索與判斷。

用法：
    # 轉成 md 表格，輸出到 stdout 或 --out
    python3 render_materials.py --spots materials/spots.json --food materials/food.json --out plan/09_materials.md

    # 正規化 JSON 檔本身（固定欄位順序、縮排、sources 單行），原地覆寫
    python3 render_materials.py --spots materials/spots.json --food materials/food.json --rewrite
"""

import argparse
import json
import sys

SPOT_FIELD_ORDER = [
    "id", "name", "name_local", "category", "audience", "why", "duration_min",
    "friendliness", "open_hours", "closed_on", "fee", "booking_required",
    "rainy_day_ok", "sources",
]
AREA_FIELD_ORDER_SPOTS = ["id", "name", "summary", "nearest_station", "spots"]
ROOT_FIELD_ORDER_SPOTS = ["version", "destination", "last_verified", "areas"]

FOOD_PICK_FIELD_ORDER = [
    "id", "name", "name_local", "category", "audience", "near_spot", "walk_min",
    "price_band", "signature", "why", "caution", "rainy_day_ok", "sources",
]
AREA_FIELD_ORDER_FOOD = ["id", "picks"]
ROOT_FIELD_ORDER_FOOD = ["version", "areas"]

SOURCE_FIELD_ORDER = ["title", "site", "url", "published", "tier"]
FRIENDLINESS_FIELD_ORDER = ["score", "notes"]


def reorder(obj, order):
    """依指定順序重排 dict 欄位；不在 order 清單內的欄位保留在原順序之後（不遺失資料）。"""
    if not isinstance(obj, dict):
        return obj
    result = {}
    for key in order:
        if key in obj:
            result[key] = obj[key]
    for key in obj:
        if key not in result:
            result[key] = obj[key]
    return result


def normalize_spots(data):
    data = reorder(data, ROOT_FIELD_ORDER_SPOTS)
    areas = []
    for area in data.get("areas", []):
        area = reorder(area, AREA_FIELD_ORDER_SPOTS)
        spots = []
        for spot in area.get("spots", []):
            spot = reorder(spot, SPOT_FIELD_ORDER)
            if "friendliness" in spot:
                spot["friendliness"] = reorder(spot["friendliness"], FRIENDLINESS_FIELD_ORDER)
            if "sources" in spot:
                spot["sources"] = [reorder(s, SOURCE_FIELD_ORDER) for s in spot["sources"]]
            spots.append(spot)
        area["spots"] = spots
        areas.append(area)
    data["areas"] = areas
    return data


def normalize_food(data):
    data = reorder(data, ROOT_FIELD_ORDER_FOOD)
    areas = []
    for area in data.get("areas", []):
        area = reorder(area, AREA_FIELD_ORDER_FOOD)
        picks = []
        for pick in area.get("picks", []):
            pick = reorder(pick, FOOD_PICK_FIELD_ORDER)
            if "sources" in pick:
                pick["sources"] = [reorder(s, SOURCE_FIELD_ORDER) for s in pick["sources"]]
            picks.append(pick)
        area["picks"] = picks
        areas.append(area)
    data["areas"] = areas
    return data


def dump_json_with_inline_sources(data):
    """自訂 JSON 序列化：一般用 json.dumps(indent=2)，但把每個 source 物件壓成單行。

    做法：先用標準 json.dumps 產生多行版本，再對 sources 陣列做後處理，
    偵測 "sources": [ ... ] 區塊並把每個物件重新序列化成單行插入。
    為了保持簡單可靠（不做脆弱的字串正則替換整個 sources 區塊），
    改用遞迴的自訂 pretty-printer，精準控制何時單行、何時多行。
    """
    return _pretty(data, indent=0)


def _pretty(obj, indent):
    pad = "  " * indent
    pad_in = "  " * (indent + 1)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            items.append(f'{pad_in}{json.dumps(k, ensure_ascii=False)}: {_pretty(v, indent + 1)}')
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        # sources 陣列（每個元素是含 title/site/url/published/tier 的物件）採單行
        if all(isinstance(el, dict) and set(el.keys()) <= set(SOURCE_FIELD_ORDER) | {"tier"} and "url" in el for el in obj):
            lines = [pad_in + json.dumps(el, ensure_ascii=False, sort_keys=False) for el in obj]
            return "[\n" + ",\n".join(lines) + "\n" + pad + "]"
        items = [pad_in + _pretty(el, indent + 1) for el in obj]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False)


def rewrite_json_file(path, normalize_fn):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data = normalize_fn(data)
    text = dump_json_with_inline_sources(data)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")  # 檔尾保留換行
    return data


def render_spots_md(data):
    lines = []
    dest = data.get("destination", "")
    lines.append(f"# 景點素材庫｜{dest}")
    lines.append("")
    lines.append(f"最後驗證日期：{data.get('last_verified', '')}")
    lines.append("")
    for area in data.get("areas", []):
        lines.append(f"## {area.get('name', area.get('id', ''))}")
        lines.append("")
        lines.append(area.get("summary", ""))
        lines.append("")
        lines.append(f"最近車站：{area.get('nearest_station', '')}")
        lines.append("")
        lines.append("| 名稱 | 類別 | 客群 | 停留(分) | 友善度 | 開放時間 | 需預約 | 雨天可去 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for spot in area.get("spots", []):
            friendliness = spot.get("friendliness", {})
            lines.append(
                f"| {spot.get('name', '')} | {spot.get('category', '')} | "
                f"{'/'.join(spot.get('audience', []))} | {spot.get('duration_min', '')} | "
                f"{'★' * int(friendliness.get('score', 0))} | {spot.get('open_hours', '')} | "
                f"{'是' if spot.get('booking_required') else '否'} | "
                f"{'是' if spot.get('rainy_day_ok') else '否'} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def render_food_md(data, spots_data=None):
    spot_name_lookup = {}
    if spots_data:
        for area in spots_data.get("areas", []):
            for spot in area.get("spots", []):
                spot_name_lookup[spot.get("id")] = spot.get("name", spot.get("id"))

    lines = []
    lines.append("# 美食素材庫")
    lines.append("")
    for area in data.get("areas", []):
        lines.append(f"## {area.get('id', '')}")
        lines.append("")
        lines.append("| 店名 | 類別 | 客群 | 鄰近景點 | 步行(分) | 價位帶 | 招牌 |")
        lines.append("|---|---|---|---|---|---|---|")
        for pick in area.get("picks", []):
            near_spot_id = pick.get("near_spot", "")
            near_spot_name = spot_name_lookup.get(near_spot_id, near_spot_id)
            lines.append(
                f"| {pick.get('name', '')} | {pick.get('category', '')} | {pick.get('audience', '')} | "
                f"{near_spot_name} | {pick.get('walk_min', '')} | {pick.get('price_band', '')} | "
                f"{pick.get('signature', '')} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="把 spots.json / food.json 轉成 md 表格，並可用 --rewrite 正規化 JSON 本身。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--spots", required=True, help="spots.json 路徑")
    parser.add_argument("--food", required=True, help="food.json 路徑")
    parser.add_argument("--out", default=None, help="輸出 md 檔路徑；省略則印到 stdout")
    parser.add_argument("--rewrite", action="store_true", help="正規化 JSON 檔本身（固定欄位順序、縮排、sources 單行），原地覆寫，不輸出 md")
    args = parser.parse_args()

    try:
        with open(args.spots, "r", encoding="utf-8") as f:
            spots_data = json.load(f)
        with open(args.food, "r", encoding="utf-8") as f:
            food_data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"讀取/解析輸入檔失敗：{e}", file=sys.stderr)
        sys.exit(2)

    if args.rewrite:
        spots_data = rewrite_json_file(args.spots, normalize_spots)
        food_data = rewrite_json_file(args.food, normalize_food)
        print(f"已正規化並覆寫：{args.spots}, {args.food}")
        sys.exit(0)

    spots_data = normalize_spots(spots_data)
    food_data = normalize_food(food_data)

    md = render_spots_md(spots_data) + "\n---\n\n" + render_food_md(food_data, spots_data)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"已輸出：{args.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
