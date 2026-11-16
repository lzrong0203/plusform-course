# 1-23 第①圈：把帳讀回來（正確版）
from pathlib import Path

p = Path(__file__).parent / "ledger.txt"
total = 0
with open(p, encoding="utf-8") as f:
    for line in f:
        row = line.rstrip("\n")
        d, item, amount = row.split(",")
        print(d, item, amount, "元")
        total += int(amount)
print("合計", total, "元")
