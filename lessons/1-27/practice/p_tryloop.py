# 矯正包練習：迴圈裡的 try 和 except（1-22）：出錯的那一次跳到 except，迴圈繼續下一個
# 先不要跑。在紙上寫下最後一行印出什麼，寫好再在帳本資料夾打 uv run lessons/1-27/practice/p_tryloop.py，對答案。
# 想一想：return 如果縮進 for 底下，會印出什麼？改改看再跑一次（改完記得改回來）。
def add_up(texts):
    total = 0
    bad = 0
    for t in texts:
        try:
            total = total + int(t)
        except ValueError:
            bad = bad + 1
    return total, bad


print(add_up(["50", "?", "70", "八十"]))
