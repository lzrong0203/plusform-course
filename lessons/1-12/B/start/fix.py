# Lv1 上關卡（卷 B）　第一部分（讀程式）：修好這支程式（3 題）
# 熊的飲料記錄：一直問一杯多少錢，打 q 就停，最後印出喝了幾杯、一共多少錢。
# 不小心多按一下 Enter（什麼都沒打的一行）的時候，這一次跳過，也不算一杯。
# 在帳本資料夾打 uv run lessons/1-12B/fix.py，依序打 45、60、q，修好以後要印出這兩行：
#   一共 2 杯
#   合計 105 元
# 跑起來跳出錯誤訊息，就從最下面一行看起；修好一個，存檔，再跑一次。
# 跑得起來以後，再試一次：打 45、直接按 Enter、60、q，也要印出一模一樣的兩行。
count = 0
mony = 0
while True:
    text = input("一杯多少錢，打 q 結束：")
    count = count + 1
    if text == "q"
        break
    if text == "":
        continue
    money = money + int(text)
print("一共", count, "杯")
print("合計", money, "元")
