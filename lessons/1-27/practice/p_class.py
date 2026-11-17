# 矯正包練習：@dataclass 的 Entry（1-24）、sum 加起來（1-17）
# 1. 在下面寫 @dataclass 和 class Entry，三個欄位：date（文字）、item（文字）、amount（整數）。
# 2. 寫好在帳本資料夾打 uv run lessons/1-27/practice/p_class.py，要印出這三行：
#    Entry(date='11/03', item='午餐', amount=120)
#    公車 15
#    2 135
from dataclasses import dataclass

# 在這裡寫 Entry


lunch = Entry("11/03", "午餐", 120)
bus = Entry("11/04", "公車", 15)
print(lunch)
print(bus.item, bus.amount)
book = [lunch, bus]
print(len(book), sum(e.amount for e in book))
