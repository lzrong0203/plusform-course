# 1-27 第一部分（卷 A）　找 bug（3 題）
# 熊的 11 月月報：從一整本帳裡挑出 11 月的帳，算筆數和合計，再找出最大的一筆。
# 這支程式跑得起來，可是有三個地方寫錯了（三個 bug）。先讀程式、先想，再動手改；改一個，存檔，跑一次。
# 在帳本資料夾打 uv run lessons/1-27/fix.py，三個都改好以後要印出這三行：
#   11 月共 3 筆，合計 415 元
#   11 月共 3 筆，合計 415 元
#   最大的一筆：電影 280 元
# 第二行是同一個月再算一次，結果要跟第一行一模一樣。日期一律寫成「月/日」，例如 11/03。
from dataclasses import dataclass


@dataclass
class Entry:
    date: str
    item: str
    amount: int


def month_of(entries, month, picked=[]):
    """交回 month 這個月（例如 "11"）的那幾筆，照原本的順序。"""
    for e in entries:
        if month in e.date:
            picked.append(e)
    return picked


def biggest(entries):
    """交回金額最大的那一筆。"""
    best = entries[0]
    for e in entries[1:]:
        if e.amount < best.amount:
            best = e
    return best


book = [Entry("10/11", "文具", 50), Entry("11/03", "午餐", 120), Entry("11/05", "電影", 280), Entry("11/08", "公車", 15)]
for _ in range(2):
    nov = month_of(book, "11")
    print(f"11 月共 {len(nov)} 筆，合計 {sum(e.amount for e in nov)} 元")
top = biggest(nov)
print(f"最大的一筆：{top.item} {top.amount} 元")
