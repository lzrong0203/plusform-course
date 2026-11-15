# Lv1 上關卡　第一部分（讀程式）：修好這支程式（3 題）
# 熊的記帳程式：一直問金額，打 q 就停，最後印出記了幾筆、一共多少。
# 不小心多按一下 Enter（什麼都沒打的一行）的時候，這一次跳過，也不算一筆。
# 在帳本資料夾打 uv run lessons/1-12/fix.py，依序打 120、85、q，修好以後要印出這兩行：
#   一共 2 筆
#   合計 205 元
# 跑起來跳出錯誤訊息，就從最下面一行看起；修好一個，存檔，再跑一次。
# 跑得起來以後，再試一次：打 120、直接按 Enter、85、q，也要印出一模一樣的兩行。
count = 0
totl = 0
while True
    text = input("金額，打 q 結束：")
    count = count + 1
    if text == "q":
        break
    if text == "":
        continue
    total = total + int(text)
print("一共", count, "筆")
print("合計", total, "元")
