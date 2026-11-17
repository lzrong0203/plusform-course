# 1-24 第③圈：正確版（照 docstring 只寫 biggest，沒有多的類別）
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

    def biggest(self):
        """交回金額最大的那一筆 Entry；帳本是空的，交回 None。"""
        best = None
        for e in self.entries:
            if best is None or e.amount > best.amount:
                best = e
        return best
