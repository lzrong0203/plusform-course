# 矯正包練習：光禿禿的 except 會把錯吞掉（1-22）
# 先不要跑。在紙上寫下最後一行印出什麼；再想一想：只看這個合計，你看得出哪幾筆有問題嗎？
# 寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_swallow.py 對答案。


def to_yuan(text):
    try:
        return int(text)
    except:
        return 0


total = 0
for t in ["300", "兩百", "45", "-x"]:
    total = total + to_yuan(t)
print("合計", total)
