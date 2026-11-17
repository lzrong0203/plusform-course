# 矯正包練習：list 交進函式，函式裡的名字和外面的名字指著同一個盒子（1-18）
# 先不要跑。在紙上畫盒子和名牌，寫下最後兩行各印出什麼，寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_listarg.py 對答案。


def add_fee(costs, fee):
    costs.append(fee)
    return len(costs)


nov = [120, 80]
n = add_fee(nov, 30)
print(n)
print(nov)
