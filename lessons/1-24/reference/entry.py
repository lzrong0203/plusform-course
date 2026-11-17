# 1-24 第①圈：一筆帳寫成 Entry 物件（正確版）
from dataclasses import dataclass

# 在這裡寫：@dataclass，再寫 class Entry，三個欄位 date（文字）、item（文字）、amount（整數）
@dataclass
class Entry:
    date: str
    item: str
    amount: int


lunch = Entry("11/03", "午餐", 120)
bus = Entry("11/04", "公車", 15)
print(lunch)
print(bus.item, bus.amount)
print(lunch.amount + bus.amount)
