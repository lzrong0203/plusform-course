# 1-8 第③圈：替 over_budget() 寫 5 條檢查（assert）
#
# 需求卡：over_budget(spent, budget) 告訴你「超過預算了嗎」，交回 True 或 False。
#   spent 是花了多少，budget 是預算。花的比預算多，才算超過；剛好花到預算，不算超過。
#
# 課程藏了 3 個寫錯的 over_budget()。你寫的 assert 要做到：
#   在正確版上全部成立，在每一個壞版本上，至少有一條不成立。
#
# 寫法：assert 後面接一件「一定要成立的事」。比較一不一樣要用兩個等號 ==（一個等號是「放進去」）。
#   True、False 不加引號，第一個字母大寫。
#
# 寫完先在帳本資料夾跑一次：uv run lessons/1-8/checks_budget.py
#   它用的是同一個資料夾裡的 budget.py（課程的正確版）。什麼都沒印出來，代表每一條都成立。
# 再回到課程資料夾打：uv run check.py 1-8

# 下面這一行是在說「要用 budget.py 裡的 over_budget」，要留著，不要刪掉
from budget import over_budget

# 第 1 條是範例，可以留著（算在 5 條裡）：
assert over_budget(1200, 1000) == True

# 換你寫（至少再 4 條）：
