# 矯正包練習：兩層迴圈，print 縮在哪一層就屬於哪一層（1-11）
# 先不要跑。在紙上寫下：上面這一段一共印出幾行？最後一行是什麼？
# 再用 uv run lessons/1-12/practice/p_nested.py 跑，對答案。
# 對了以後，把最後一行的 print 往右縮四格（縮進內層），再寫一次一共印出幾行，再跑。
n = 0
for week in range(1, 4):
    for day in range(3):
        n = n + 1
    print("第", week, "週", n)
