# 矯正包練習：any 和 all（1-20）
# 先不要跑。在紙上寫下最後四行 print 各印出什麼（True 或 False），寫好再在帳本資料夾打 uv run lessons/1-27/practice/p_any.py，對答案。
# （any：只要有一個成立就是 True；all：每一個都成立才是 True。）
amounts = [120, 15, 180]
print(any(a > 150 for a in amounts))
print(all(a > 150 for a in amounts))
print(all(a > 10 for a in amounts))
print(any(a > 500 for a in amounts))
