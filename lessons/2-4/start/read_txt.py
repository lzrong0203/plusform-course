# 2-4 第①圈：1-23 的讀法（一行一筆，用逗號切開）。備註裡有逗號，就切壞了
from pathlib import Path

p = Path(__file__).parent / "ledger.txt"
with open(p, encoding="utf-8") as f:
    for line in f:
        d, item, amount, note = line.rstrip("\n").split(",")
        print(d, item, amount, note)
