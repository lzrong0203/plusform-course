# 1-13 正確版：帳目小工具（課程寫好的函式，學員只呼叫、不用看懂 def 那一行，1-18 才教）
# 需求卡：remove_last 刪掉最後一筆，交回被刪掉的那一筆；
#         index_of_max 交回最大的那一筆在第幾個位置（索引，從 0 數），一樣大的有好幾筆，交回最前面那一筆；
#         查最大的時候，不能動到原本的順序。


def remove_last(amounts):
    return amounts.pop()


def index_of_max(amounts):
    where = 0
    for i, cost in enumerate(amounts):
        if cost > amounts[where]:
            where = i
    return where
