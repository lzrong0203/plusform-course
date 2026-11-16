# 1-23 第①圈：把帳寫進檔案
# 1. 第 6 行的 p 改成「跟著這個檔走」的寫法：Path(__file__).parent / "ledger.txt"
# 2. 在下面用 with open 把每一筆寫成一行：日期,項目,金額（最後要換行），記得寫 encoding="utf-8"
from pathlib import Path

p = "ledger.txt"
entries = [("11/03", "午餐", 120),
           ("11/04", "公車", 15),
           ("11/05", "晚餐", 180)]

# 在這裡寫 with open(p, "w", ...) 那幾行：


print("存好了")
