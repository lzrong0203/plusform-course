# 1-24 第②圈：跟家教一起寫 Ledger（帶我寫：每一步你先說、先寫，家教再說對不對）
from dataclasses import dataclass


@dataclass
class Entry:
    date: str
    item: str
    amount: int


class Ledger:
    """一本帳本：裡面放很多筆 Entry。"""

    # 換你寫（照 tutor.md 跟家教一步一步來）：
    # 1. 每本帳本要有自己的 entries（一開始是空的 list）
    # 2. add(self, entry)：把一筆 Entry 放進 entries 最後面
    # 3. total(self)：交回所有金額的合計（沒有帳交回 0）


nov = Ledger()
dec = Ledger()
nov.add(Entry("11/03", "午餐", 120))
nov.add(Entry("11/04", "公車", 15))
print(len(nov.entries), len(dec.entries))
print(nov.total(), dec.total())
