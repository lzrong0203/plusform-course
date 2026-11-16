# 1-23 第①圈：把帳讀回來
# 1. 第 6 行的 p 一樣改成跟著這個檔走的寫法
# 2. 用 with open 一行一行讀：拿掉最後的換行、用逗號切開，印出「日期 項目 金額 元」，金額加進 total
from pathlib import Path

p = "ledger.txt"
total = 0

# 在這裡寫 with open(p, ...) 那幾行：


print("合計", total, "元")
