# 矯正包練習：推導式（先看 for、再看 if、最後看最前面放進去的）和 zip（兩串一格一格配成一對）（1-17）
# 先不要跑。在紙上寫下最後三行 print 各印出什麼，寫好再在帳本資料夾打 uv run lessons/1-C3/practice/p_comp.py，對答案。
dates = ["11/01", "11/02", "11/03"]
amounts = [150, 40, 200]
print([a for a in amounts if a >= 100])
print([a + 10 for a in amounts])
for d, a in zip(dates, amounts):
    print(d, a)
