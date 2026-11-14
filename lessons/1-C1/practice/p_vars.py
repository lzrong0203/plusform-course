# 矯正包練習：等號是「放進去」、右邊先算（1-2）
# 先不要跑。在紙上畫追蹤表：每一行跑完以後，money 和 cost 各是多少？最後一行印出什麼？
# 寫好再在帳本資料夾打 uv run lessons/1-C1/practice/p_vars.py 對答案（只看得到最後印出的，中間的值用追蹤表對）。
money = 300
cost = 80
money = money - cost
cost = cost * 2
money - cost
money = money - cost
print(money, cost)
