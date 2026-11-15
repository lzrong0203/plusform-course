# 矯正包練習：if、elif、else 從上往下看，第一個成立的才做（1-9）
# 先不要跑。在紙上寫下這一支會印出哪幾行。再把第 5 行的 score 改成 95、改成 40，各寫一次。
# 寫好再在帳本資料夾打 uv run lessons/1-C2/practice/p_if.py 對答案（改了數字要存檔再跑）。
# 對不上的那一次，回 1-9 影片再看一次那一段（時間寫在矯正包.md）。
score = 75
if score >= 90:
    print("優等")
elif score >= 60:
    print("及格")
else:
    print("再加油")
print("分數是", score)
