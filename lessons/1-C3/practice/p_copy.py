# 矯正包練習：copy() 做出另一個 list；insert、remove、pop 只改它自己（1-13、1-16）
# 先不要跑。在紙上替 a 和 b 各畫一排格子（copy 以後是兩排），每跑一行就改一次。
# 寫下最後兩行 print 各印出什麼，寫好再在帳本資料夾打 uv run lessons/1-C3/practice/p_copy.py，對答案。
a = [60, 120, 85]
b = a.copy()
a.insert(1, 40)
b.remove(120)
last = a.pop()
print(a, last)
print(b)
