#!/usr/bin/env python3
"""scrub_check.py — 從私有原始輸入抽出個資 token，掃描待版控檔案是否外洩。

依據 references/privacy.md 的隱私分層原則：使用者提供的原始資訊（trips/{trip}/private/ 下）
不得出現在任何即將進版控的檔案中（trip_context.json、progress.md、materials/*.json、plan/*.md）。

本 script 從指定的 private 原始輸入檔（任意文字檔：md/txt/貼上的訂房確認信等）抽出以下
8 類 token，並掃描待版控檔案是否含這些字串，命中即報錯：
  1. 訂房確認號 / 訂單編號（如 Booking Reference、確認碼）
  2. 訂房人姓名（Name / 姓名 / 訂房人 標籤後的值）
  3. 航班號（2 碼航空公司代碼 + 2~4 碼數字，如 BR225、CI702）
  4. 飯店/住宿名稱（Hotel / 飯店 / 民宿 標籤後的值；另有無標籤規則，
     可抓出訂房確認信裡未帶標籤的 "X Hotel" 與中文「XX飯店」）
  5. 電話號碼（含國際冠碼、市話、手機各種格式）
  6. Email 地址
  7. 護照號碼（Passport No. 標籤後的值）
  8. 門牌地址（Address / 地址 標籤後的值）

只使用 Python 3 標準庫，不 import 任何第三方套件。
只做字串比對，不做語意判斷。

用法：
    python3 scrub_check.py --input private/input/booking_confirmation.txt \\
        --targets trip_context.json progress.md materials/spots.json materials/food.json plan/*.md

    # 掃描整個目錄（遞迴找 .md / .json）
    python3 scrub_check.py --input private/input/*.txt --targets-dir .

Exit code：
    0 = 未發現任何 token 外洩
    1 = 發現至少一處外洩
    2 = 執行本身失敗（找不到輸入檔等）
"""

import argparse
import glob
import os
import re
import sys

LABEL_PATTERNS = {
    "訂房人姓名": [
        r"(?:姓名|訂房人|旅客姓名|Guest\s*Name|Name)\s*[:：]\s*([^\n,，、]+)",
    ],
    "飯店/住宿名稱": [
        r"(?:飯店|酒店|民宿|Hotel|Property)\s*(?:名稱)?\s*[:：]\s*([^\n,，、]+)",
    ],
    "護照號碼": [
        r"(?:護照號碼|Passport\s*(?:No\.?|Number))\s*[:：]\s*([A-Za-z0-9]{6,12})",
    ],
    "門牌地址": [
        r"(?:地址|Address)\s*[:：]\s*([^\n]+)",
    ],
    "訂房確認號": [
        r"(?:確認號|確認碼|訂單編號|訂房編號|Booking\s*Reference|Confirmation\s*(?:No\.?|Number|Code)|PNR)\s*[:：]\s*([A-Za-z0-9\-]{5,15})",
    ],
}

GENERIC_PATTERNS = {
    "Email": re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    "電話號碼": re.compile(r"(?:\+?\d{1,3}[-\s]?)?(?:\(0\)|0)?\d{1,4}[-\s]?\d{3,4}[-\s]?\d{3,4}"),
    "航班號": re.compile(r"\b[A-Z]{2}\d{2,4}\b"),
    # 住宿名稱在真實訂房確認信裡幾乎不帶標籤（"reservation with X Hotel"、
    # "Greetings from X Hotel"、行程表裡直接寫店名），只靠 LABEL_PATTERNS 會整類漏掉。
    "住宿名稱（無標籤）": re.compile(
        r"\b(?:[A-Z][A-Za-z'\u2019\-]*\s+){0,4}"
        r"(?:Hotel|Hostel|Inn|Resort|Residence|Suites|Guesthouse|Guest\s*House|Motel)\b"
    ),
    "住宿名稱（中文無標籤）": re.compile(
        r"[\u4e00-\u9fffA-Za-z0-9]{2,12}(?:大飯店|飯店|酒店|旅館|民宿|會館)"
    ),
}

# 短於此長度的 token 容易誤判/雜訊過多，不納入掃描。
# 標籤式抽取（姓名等）已由標籤錨定，誤判風險低，門檻可以放低（中文姓名常只有 2~3 字）；
# 無標籤的泛用規則（email/電話/航班號）門檻較高，避免抓到無意義的短碎片。
MIN_TOKEN_LEN_LABELED = 2
MIN_TOKEN_LEN_GENERIC = 4


def extract_tokens(text):
    """回傳 {category: set(tokens)}"""
    tokens = {}

    for category, patterns in LABEL_PATTERNS.items():
        found = set()
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                value = m.group(1).strip()
                if len(value) >= MIN_TOKEN_LEN_LABELED:
                    found.add(value)
        if found:
            tokens[category] = found

    for category, pat in GENERIC_PATTERNS.items():
        found = {m.group(0).strip() for m in pat.finditer(text) if len(m.group(0).strip()) >= MIN_TOKEN_LEN_GENERIC}
        if found:
            tokens.setdefault(category, set()).update(found)

    return tokens


def load_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def scan_target(path, tokens_by_category):
    """回傳違規清單 [(category, token, line_no, line_text), ...]"""
    hits = []
    try:
        text = load_text(path)
    except OSError as e:
        print(f"警告：無法讀取目標檔 {path}：{e}", file=sys.stderr)
        return hits

    lines = text.splitlines()
    for category, tokens in tokens_by_category.items():
        for token in tokens:
            for i, line in enumerate(lines, start=1):
                if token in line:
                    hits.append((category, token, i, line.strip()))
    return hits


def expand_targets(targets, targets_dir):
    paths = []
    for pattern in targets or []:
        matched = glob.glob(pattern, recursive=True)
        paths.extend(matched if matched else [pattern])
    if targets_dir:
        for root, _dirs, files in os.walk(targets_dir):
            if "private" in root.split(os.sep):
                continue  # private/ 本身不是待版控檔，不需要掃描自己
            for fn in files:
                if fn.endswith((".md", ".json")):
                    paths.append(os.path.join(root, fn))
    # 去重並排除不存在的檔案
    seen = []
    for p in paths:
        if os.path.isfile(p) and p not in seen:
            seen.append(p)
    return seen


def main():
    parser = argparse.ArgumentParser(
        description="從 private 原始輸入抽 token，掃描待版控檔案是否外洩個資。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", nargs="+", required=True, help="private 原始輸入檔路徑（可多個，可用 glob）")
    parser.add_argument("--targets", nargs="*", default=None, help="待掃描的目標檔路徑或 glob（trip_context.json / progress.md / materials/*.json / plan/*.md）")
    parser.add_argument("--targets-dir", default=None, help="待掃描的目錄，遞迴掃描其中 .md / .json（會自動跳過 private/ 子目錄）")
    args = parser.parse_args()

    if not args.targets and not args.targets_dir:
        print("必須指定 --targets 或 --targets-dir 至少一項", file=sys.stderr)
        sys.exit(2)

    input_paths = []
    for pattern in args.input:
        matched = glob.glob(pattern)
        input_paths.extend(matched if matched else [pattern])

    all_tokens = {}
    for path in input_paths:
        if not os.path.isfile(path):
            print(f"輸入檔不存在：{path}", file=sys.stderr)
            sys.exit(2)
        text = load_text(path)
        tokens = extract_tokens(text)
        for category, found in tokens.items():
            all_tokens.setdefault(category, set()).update(found)

    total_tokens = sum(len(v) for v in all_tokens.values())
    print(f"從 {len(input_paths)} 份輸入檔抽出 {total_tokens} 個候選 token，分 {len(all_tokens)} 類：")
    for category, found in all_tokens.items():
        print(f"  - {category}：{len(found)} 個")

    target_paths = expand_targets(args.targets, args.targets_dir)
    if not target_paths:
        print("警告：沒有找到任何待掃描的目標檔", file=sys.stderr)

    all_hits = []
    for target in target_paths:
        hits = scan_target(target, all_tokens)
        for category, token, line_no, line_text in hits:
            all_hits.append((target, category, token, line_no, line_text))

    print()
    if all_hits:
        print(f"=== 發現 {len(all_hits)} 處疑似個資外洩 ===")
        for target, category, token, line_no, line_text in all_hits:
            print(f"  [ERROR] {target}:{line_no} 含 {category} token '{token}' -> {line_text}")
        sys.exit(1)
    else:
        print("掃描完成，未發現外洩。")
        sys.exit(0)


if __name__ == "__main__":
    main()
