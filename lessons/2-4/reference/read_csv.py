# 2-4 第①圈：用 csv 模組把 ledger.csv 讀回來
import csv
from pathlib import Path

p = Path(__file__).parent / "ledger.csv"
total = 0
with open(p, encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        print(row["日期"], row["項目"], row["金額"], row["備註"])
        total += int(row["金額"])

print("合計", total, "元")
