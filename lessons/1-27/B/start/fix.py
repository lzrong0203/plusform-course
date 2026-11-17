# 1-27 第一部分（卷 B）　找 bug（3 題）
# 熊的 12 月月報：從一整本帳裡挑出 12 月的帳，算筆數和合計，再找出最便宜的一筆。
# 這支程式跑得起來，可是有三個地方寫錯了（三個 bug）。先讀程式、先想，再動手改；改一個，存檔，跑一次。
# 在帳本資料夾打 uv run lessons/1-27B/fix.py，三個都改好以後要印出這三行：
#   12 月共 3 筆，合計 495 元
#   12 月共 3 筆，合計 495 元
#   最便宜的一筆：飲料 50 元
# 第二行是同一個月再算一次，結果要跟第一行一模一樣。日期一律寫成「月/日」，例如 12/01。
from dataclasses import dataclass


@dataclass
class Entry:
    date: str
    item: str
    amount: int


def month_of(entries, month, picked=[]):
    """交回 month 這個月（例如 "12"）的那幾筆，照原本的順序。"""
    for e in entries:
        if month in e.date:
            picked.append(e)
    return picked


def cheapest(entries):
    """交回金額最小的那一筆。"""
    best = entries[0]
    for e in entries[1:]:
        if e.amount > best.amount:
            best = e
    return best


book = [Entry("11/12", "雨傘", 450), Entry("12/01", "早餐", 65), Entry("12/02", "書", 380), Entry("12/05", "飲料", 50)]
for _ in range(2):
    dec = month_of(book, "12")
    print(f"12 月共 {len(dec)} 筆，合計 {sum(e.amount for e in dec)} 元")
low = cheapest(dec)
print(f"最便宜的一筆：{low.item} {low.amount} 元")
