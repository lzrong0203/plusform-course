# 1-22 第③圈：替 to_yuan 寫檢查
# 課程藏了 3 個 AI 寫錯的版本（範例示意）。你寫的檢查（至少 3 條）要做到：
#   在正確的版本上全部成立，在每一個寫錯的版本上，至少有一條不成立。
# 一般的金額用 assert 寫一行；「應該丟出錯誤」的，用下面這個 try 的寫法，整段算一條：
#   try 裡呼叫它 → 丟出 ValueError，就跳到 except，檢查訊息裡有沒有那段字
#                → 沒丟出錯誤，就走 else，assert False（這一條不成立）
# except 後面一定要寫明 ValueError：光禿禿的 except: 什麼錯都接住，丟錯類型的版本就抓不到了。
# 寫完先在帳本資料夾跑一次：uv run lessons/1-22/checks_money.py
#   它用的是同一個資料夾裡你的 money.py。什麼都沒印出來，代表每一條都成立。
# 再回到課程資料夾打：uv run check.py 1-22

# 下面這一行是在說「要用 money.py 裡的 to_yuan」，要留著，不要刪掉
from money import to_yuan

# 範例 1（可以留著，算在 3 條裡）：一般的金額
assert to_yuan("1,200元") == 1200

# 範例 2（可以留著，算在 3 條裡）：負數要丟 ValueError，訊息裡要有那個值
# （money.py 還沒加上負數的 raise 以前，這一條不成立；第一圈加好以後才會成立）
try:
    to_yuan("-35")
except ValueError as e:
    assert "-35" in str(e)
else:
    assert False

# 換你寫（至少再 1 條）：看不懂的金額（像 一百）也要丟 ValueError，不能被吞掉、交回別的值
