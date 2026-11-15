# 矯正包練習：錯誤訊息從最下面一行看起（1-7）
# 先在帳本資料夾打 uv run lessons/1-12/practice/p_traceback.py，打 50、按 Enter。
# 跳出錯誤訊息以後，先在紙上寫下：最後一行冒號前面是哪一種錯？往上看，是第幾行？
# 再修好它：打 50、30、q，要印出「一共 80 元」。
total = 0
while True:
    text = input("金額，打 q 結束：")
    if text == "q":
        break
    total = total + text
print("一共", total, "元")
