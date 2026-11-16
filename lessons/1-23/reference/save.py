# 1-23 第①圈：把帳寫進檔案（正確版）
from pathlib import Path

p = Path(__file__).parent / "ledger.txt"
entries = [("11/03", "午餐", 120),
           ("11/04", "公車", 15),
           ("11/05", "晚餐", 180)]

with open(p, "w", encoding="utf-8") as f:
    for d, item, amount in entries:
        f.write(f"{d},{item},{amount}\n")
print("存好了")
