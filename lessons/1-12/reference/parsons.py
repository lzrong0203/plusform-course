# Lv1 上關卡　第一部分：拼圖的參考排法（排法不只一種，check 照跑出來的結果判）
bank = 0
week = 0
while True:
    week = week + 1
    bank = bank + 150
    if bank >= 500:
        break
print("第", week, "週存到", bank, "元")
