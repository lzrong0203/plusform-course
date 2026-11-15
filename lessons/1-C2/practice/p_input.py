# 矯正包練習：input 交回的一定是字串、int() 變成整數（1-6）
# 先不要跑。假設跑的時候，你先打 7、按 Enter，再打 8、按 Enter。在紙上寫下最後三行 print 各印出什麼。
# 寫好再在帳本資料夾打 uv run lessons/1-C2/practice/p_input.py，照上面打 7 和 8，對答案。
# 對不上的那一行，回 1-6 影片再看一次那一段（時間寫在矯正包.md）。
a = input("第一個：")
b = input("第二個：")
print(a + b)
print(b + a)
print(int(a) + int(b))
