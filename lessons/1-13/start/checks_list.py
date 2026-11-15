# 1-13 第③圈：替課程的 remove_last() 和 index_of_max() 寫檢查（註解寫要求、assert 寫一定要成立的事）
#
# 需求卡：
#   remove_last(amounts)：刪掉最後一筆，交回被刪掉的那一筆（amounts 少一筆）。
#   index_of_max(amounts)：交回最大的那一筆在第幾個位置（索引，從 0 數）；
#       一樣大的有好幾筆，交回最前面那一筆；查的時候，不能動到原本的順序。
#
# 課程藏了 3 個寫錯的版本。你寫的 assert（至少 5 條）要做到：
#   在正確版上全部成立，在每一個壞版本上，至少有一條不成立。
#
# 寫法：每一段先用一行註解（# 開頭）寫你要檢查什麼，下面再寫 assert。
#   list 也可以用兩個等號比：assert a == [120, 85] 是在問「a 現在是不是這兩筆、而且是這個順序」。
#   要檢查呼叫完以後 list 變成什麼樣子，先把 list 放進一個名字（例如 a），呼叫完再比 a。
#
# 寫完先在帳本資料夾跑一次：uv run lessons/1-13/checks_list.py
#   它用的是同一個資料夾裡的 entries.py（課程的正確版）。什麼都沒印出來，代表每一條都成立。
# 再回到課程資料夾打：uv run check.py 1-13

# 下面這一行是在說「要用 entries.py 裡的兩個小工具」，要留著，不要刪掉
from entries import remove_last, index_of_max

# 範例（可以留著，算在 5 條裡）：刪掉最後一筆，交回那一筆
a = [120, 85, 200]
assert remove_last(a) == 200

# 換你寫（至少再 4 條）：
