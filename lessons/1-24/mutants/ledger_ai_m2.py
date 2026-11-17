# 1-24 第③圈 壞版本 2（範例示意）：先拿第一筆當最大的，帳本是空的就當掉（IndexError）
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
        best = self.entries[0]
        for e in self.entries:
            if e.amount > best.amount:
                best = e
        return best
