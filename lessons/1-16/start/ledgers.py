# 1-16 第①圈：果凍兔的兩本帳本。熊和兔想各記各的，都從一個空的 list 開始。
# 可是跑起來，兩本印出來一模一樣。改成兩本分開的帳本：熊的只有 120，兔的只有 300。
# start = [] 這一行留著；改 bear、rabbit 那兩行就好（用 copy() 或切片，或各自一個新的空 list）。
start = []
bear = start
rabbit = start
bear.append(120)
rabbit.append(300)
print("熊的帳", bear)
print("兔的帳", rabbit)
print("是同一本嗎", bear is rabbit)
