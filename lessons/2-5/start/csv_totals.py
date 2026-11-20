# 2-5 開場：CSV 版的「本月各分類合計」（2-4 學過的寫法：一筆一筆讀、用 dict 加起來）
import csv
from pathlib import Path

HERE = Path(__file__).parent
totals = {}
with open(HERE / "entries.csv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        if not row["日期"].startswith("2026-11") or not row["金額"]:
            continue   # 不是 11 月的、金額空白的，都不算
        totals[row["分類"]] = totals.get(row["分類"], 0) + int(row["金額"])
for category, total in totals.items():
    print(category, total)
