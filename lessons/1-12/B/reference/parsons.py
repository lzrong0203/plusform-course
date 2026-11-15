# Lv1 上關卡（卷 B）　第一部分：拼圖的參考排法（排法不只一種，check 照跑出來的結果判）
cups = 0
money = 0
while True:
    cups = cups + 1
    money = money + 45
    if money > 200:
        break
print("第", cups, "杯，一共", money, "元")
