# 1-26 第③圈：正確版（照 docstring：先檢查編號，沒確認只交回、不刪；編號從 1 開始，所以是 no - 1）
from dataclasses import dataclass


@dataclass
class Entry:
    date: str
    item: str
    amount: int


def delete_entry(entries, no, confirm=False):
    """刪掉第 no 筆帳，刪除前要先確認。

    輸入：entries 一串 Entry；no 是 show 印的編號（從 1 開始）；confirm 確認了沒有（預設 False）
    輸出：要刪的那一筆 Entry。confirm 是 False 只交回、不刪；是 True 才從 entries 拿掉
    編號不在 1 到筆數之間：丟 ValueError，什麼都不刪
    例子：entries 是 [午餐, 公車, 晚餐]
        delete_entry(entries, 2) 交回公車，entries 還是三筆
        delete_entry(entries, 2, confirm=True) 交回公車，entries 剩 [午餐, 晚餐]
    """
    if no < 1 or no > len(entries):
        raise ValueError(f"沒有第 {no} 筆")
    if not confirm:
        return entries[no - 1]
    return entries.pop(no - 1)
