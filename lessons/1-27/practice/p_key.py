# 矯正包練習：sorted 的 key 和 lambda（1-20）、一對一對的 tuple 用 [0]、[1] 拿（1-14）
# 先不要跑。在紙上寫下最後三行 print 各印出什麼，寫好再在帳本資料夾打 uv run lessons/1-27/practice/p_key.py，對答案。
# （key=lambda p: p[1] 的意思：排的時候，每一對拿它的第二個來比；reverse=True 是大的排前面。）
pairs = [("早餐", 60), ("晚餐", 180), ("飲料", 45)]
by_money = sorted(pairs, key=lambda p: p[1])
print(by_money[0])
print(sorted(pairs, key=lambda p: p[1], reverse=True)[0][0])
print(by_money[-1][1])
