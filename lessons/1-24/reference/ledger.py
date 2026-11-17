# 1-24 第②圈：Ledger（正確版：entries 在 __init__ 裡給 self，每本帳本各有一個）
from dataclasses import dataclass


@dataclass
class Entry:
    date: str
    item: str
    amount: int


class Ledger:
    """一本帳本：裡面放很多筆 Entry。"""

    def __init__(self):
        self.entries = []

    def add(self, entry):
        self.entries.append(entry)

    def total(self):
        s = 0
        for e in self.entries:
            s += e.amount
        return s


nov = Ledger()
dec = Ledger()
nov.add(Entry("11/03", "午餐", 120))
nov.add(Entry("11/04", "公車", 15))
print(len(nov.entries), len(dec.entries))
print(nov.total(), dec.total())
