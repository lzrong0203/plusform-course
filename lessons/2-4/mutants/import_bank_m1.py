# 2-4 壞版本 m1（退款當成支出）：匯入兩家銀行的對帳單（假資料）
import csv
import re

# 兩家銀行的欄位名稱不一樣：左邊是帳本用的名字，右邊是對帳單可能用的名字
COLUMNS = {
    "日期": ["交易日期", "消費日"],
    "項目": ["摘要", "說明"],
    "金額": ["金額", "交易金額"],
}


def roc_date(text):
    """民國年的日期換成西元年：115/11/03 → 2026/11/03"""
    m = re.fullmatch(r"(\d{2,3})/(\d{1,2})/(\d{1,2})", text.strip())
    if m is None:
        raise ValueError(f"看不懂的日期：{text}")
    year = int(m.group(1)) + 1911
    return f"{year}/{int(m.group(2)):02d}/{int(m.group(3)):02d}"


def to_int(text):
    """金額的字換成整數：1,250 → 1250，-350 → -350（退款是負的）"""
    return int(re.sub(r"\D", "", text))


def pick(row, name):
    """照 COLUMNS，找出這一列裡 name 那一欄的字"""
    for col in COLUMNS[name]:
        if col in row:
            return row[col]
    raise KeyError(f"對帳單裡找不到「{name}」這一欄")


def category_of(item, keywords):
    """項目裡有哪個關鍵字，就是哪一類；都沒有就是其他"""
    for word, category in keywords.items():
        if word in item:
            return category
    return "其他"


def import_statement(path, keywords):
    """讀一份對帳單（CSV），交回一串 (日期, 項目, 分類, 金額)。

    path：對帳單的路徑；keywords：分類關鍵字，例如 {"超市": "日用品"}
    日期換成西元年（2026/11/03），金額是整數（退款是負的），空白列跳過
    """
    entries = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if not pick(row, "日期").strip():   # 空白列
                continue
            item = pick(row, "項目").strip()
            entries.append((roc_date(pick(row, "日期")), item, category_of(item, keywords), to_int(pick(row, "金額"))))
    return entries


def category_totals(entries):
    """各分類的合計：{分類: 金額加起來}（退款是負的，會扣掉）"""
    totals = {}
    for date, item, category, amount in entries:
        totals[category] = totals.get(category, 0) + amount
    return totals
