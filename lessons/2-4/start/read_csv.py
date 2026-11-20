# 2-4 第①圈：用 csv 模組把 ledger.csv 讀回來
import csv
from pathlib import Path

p = Path(__file__).parent / "ledger.csv"
total = 0
# 換你寫：with open 打開 p（encoding="utf-8"、newline=""），
#   for row in csv.DictReader(f): 每一列是一個 dict，印出日期、項目、金額、備註，金額 int(...) 加進 total

print("合計", total, "元")
