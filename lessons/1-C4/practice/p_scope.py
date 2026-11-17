# 矯正包練習：函式裡給了值的名字是小框自己的（區域變數），外面那個不會變；沒有 return，交回 None（1-19、1-18）
# 先不要跑。在紙上畫小框，寫下印出來的三行，寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_scope.py 對答案。
budget = 1000


def spend(amount):
    budget = 1000 - amount
    return budget


def note(text):
    print("記下：", text)


left = spend(300)
r = note(left)
print(left, budget)
print(r)
