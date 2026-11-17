# 1-24 第③圈：AI 交回的 ledger_ai.py（課程準備的固定版本，範例示意；不要改它）
# 熊的需求只有一個：Ledger 加上 biggest()（交回金額最大的那一筆 Entry；帳本是空的，交回 None）。
from dataclasses import dataclass


@dataclass
class Entry:
    date: str
    item: str
    amount: int


class BaseLedger:
    """所有帳本的基礎類別。"""

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


class Ledger(BaseLedger):
    """一般的帳本。"""


class MonthlyLedger(Ledger):
    """只收某一個月的帳本。"""

    def __init__(self, month):
        super().__init__()
        self.month = month

    def add(self, entry):
        if entry.date.startswith(self.month + "/"):
            super().add(entry)


class FoodLedger(Ledger):
    """只收三餐的帳本。"""

    def add(self, entry):
        if entry.item in ("早餐", "午餐", "晚餐"):
            super().add(entry)
