# 1-21 第①圈：money.py（跟 main.py 放在同一個資料夾 lessons/1-21/）
# 1. 把 main.py 裡的 total、fmt 這兩個函式「搬」過來，貼在這段註解下面
# 2. 最下面三行是 money.py 自己的檢查：只有「直接跑 money.py」的時候才要跑，
#    被 main.py import 的時候不要跑。把它們放進 if __name__ == "__main__": 下面（三行前面各空四格）
# 寫完在帳本資料夾打：uv run lessons/1-21/money.py   → 印出「money.py 自己的檢查都過了」
#                    uv run lessons/1-21/main.py    → 不會印出那一行


assert total([120, 85]) == 205
assert fmt(1250) == "1,250 元"
print("money.py 自己的檢查都過了")
