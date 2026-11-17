"""AI 交回來的 delete_entry（課程準備的固定版本，範例示意，不要改它）。"""
from dataclasses import dataclass


@dataclass
class Entry:
    date: str
    item: str
    amount: int


def delete_entry(entries, no, confirm=False):
    """刪掉第 no 筆帳，刪除前要先確認。

    輸入：entries、no（show 印的編號，從 1 開始）、confirm（預設 False）
    輸出：要刪的那一筆 Entry
      confirm 是 False：只交回，不刪
      confirm 是 True：從 entries 拿掉，也交回
    編號不在 1 到筆數之間：丟 ValueError，什麼都不刪
    例子：[午餐, 公車, 晚餐] 刪第 2 筆 → 交回公車
    """
    if no < 1 or no > len(entries):
        raise ValueError(f"沒有第 {no} 筆")
    if not confirm:
        return entries[no]
    return entries.pop(no)
