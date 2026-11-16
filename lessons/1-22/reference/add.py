# 1-22 第①圈：add.py（正確版）。跟 money.py 放在同一個資料夾。
from money import to_yuan

while True:
    text = input("金額：")
    try:
        amount = to_yuan(text)
    except ValueError as e:
        print("請再輸入一次。", e)
    else:
        print("記下", amount, "元")
        break
