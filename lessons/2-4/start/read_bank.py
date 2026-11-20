# 2-4 第①圈：讀對帳單，一筆一筆整理好
import csv
from pathlib import Path

from clean import roc_date, to_int

p = Path(__file__).parent / "bank_a.csv"
with open(p, encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        # 換你寫：日期是空的（空白列），就 continue 跳過
        print(roc_date(row["交易日期"]), row["摘要"], to_int(row["金額"]))
