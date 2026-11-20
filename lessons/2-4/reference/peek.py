# 2-4 第①圈：看看練習用的對帳單（假資料），讀進來長什麼樣子
import csv
from pathlib import Path

p = Path(__file__).parent / "bank_a.csv"
with open(p, encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        print(row["交易日期"], row["摘要"], row["金額"])
