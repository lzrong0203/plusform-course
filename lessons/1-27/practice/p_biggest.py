# 矯正包練習：找最大的那一個（1-11 的找最大值，用在 Entry 上）
# biggest 想找金額最大的那一筆，可是比較的方向寫反了。先不要跑，在紙上寫下它會交回哪一筆；
# 再在帳本資料夾打 uv run lessons/1-27/practice/p_biggest.py 對答案，最後把比較改好，要印出：晚餐 180
from dataclasses import dataclass


@dataclass
class Entry:
    item: str
    amount: int


def biggest(entries):
    best = entries[0]
    for e in entries[1:]:
        if e.amount < best.amount:
            best = e
    return best


top = biggest([Entry("早餐", 60), Entry("晚餐", 180), Entry("飲料", 45)])
print(top.item, top.amount)
