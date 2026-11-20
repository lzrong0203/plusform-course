# 範例示意：把 import_bank.py 交給 AI 寫，它交回來的樣子（課程凍結的版本，第③圈拿來驗收）
import csv
import re

DATE_COLS = ["交易日期", "消費日"]
ITEM_COLS = ["摘要", "說明"]
AMOUNT_COLS = ["金額", "交易金額"]


def _find(row, names):
    for name in names:
        if name in row:
            return row[name]
    raise KeyError(f"找不到欄位：{names}")


def parse_date(text):
    m = re.fullmatch(r"(\d{2,3})/(\d{1,2})/(\d{1,2})", text.strip())
    if not m:
        raise ValueError(f"日期格式不對：{text}")
    return f"{int(m.group(1)) + 1911}/{int(m.group(2)):02d}/{int(m.group(3)):02d}"


def parse_amount(text):
    return int(re.sub(r"\D", "", text))


def _category(item, keywords):
    for word, category in keywords.items():
        if word in item:
            return category
    return "其他"


def import_statement(path, keywords):
    """讀銀行對帳單（CSV），交回 (日期, 項目, 分類, 金額) 的 list。"""
    entries = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            date = _find(row, DATE_COLS).strip()
            if not date:
                continue
            item = _find(row, ITEM_COLS).strip()
            amount = parse_amount(_find(row, AMOUNT_COLS))
            entries.append((parse_date(date), item, _category(item, keywords), amount))
    return entries


def category_totals(entries):
    totals = {}
    for _date, _item, category, amount in entries:
        totals[category] = totals.get(category, 0) + amount
    return totals
