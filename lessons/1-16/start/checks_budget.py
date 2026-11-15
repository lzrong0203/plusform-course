# 1-16 第③圈：先寫 assert，證明 budget.py 算錯了；修好 budget.py 以後，同一條 assert 要變成成立
#
# budget.py 印出三行：11 月合計、12 月合計、固定開銷。先自己算好正確的答案：
#   固定開銷 fixed＝房租 12000＋手機 499
#   11 月 nov＝固定開銷＋午餐 120
#   12 月 dec＝固定開銷＋機票 3000
#
# 寫法：先用一行註解（# 開頭）寫你要檢查什麼，下面寫 assert，兩個等號右邊放你自己算好的數字。
#   sum(nov) 是 nov 全部加起來（1-13）。
#
# 寫完在帳本資料夾跑：uv run lessons/1-16/checks_budget.py
#   budget.py 還沒修：跳出 AssertionError，就證明它算錯了。
#   修好以後再跑一次：什麼都沒印出來（只有 budget.py 印的三行），代表每一條都成立。
# 檢查的時候回到課程資料夾打：uv run check.py 1-16
#   check 會把你的 assert 拿去跑課程的正確版和 3 個算錯的版本（第 1 個就是你拿到的 budget.py）。

# 下面這一行是在說「要用 budget.py 裡的 fixed、nov、dec」，要留著，不要刪掉
from budget import fixed, nov, dec

# 換你寫（至少 1 條）：
