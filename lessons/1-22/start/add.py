# 1-22 第①圈：記一筆帳（跟 money.py 放在同一個資料夾）。
# 現在打「一百」或「-35」，它會當掉（Traceback），或把負數記下來。
# 1. 先在 money.py 的 to_yuan 加上：金額是負數，就 raise ValueError，訊息裡放進那個值。
# 2. 再改這個檔：用 try 包住 amount = to_yuan(text)，
#    except ValueError as e：印出「請再輸入一次。」和 e，迴圈再問一次；
#    else（沒出錯）：印出「記下 120 元」這樣的一行，再 break 停下來。
# 寫完在帳本資料夾打：uv run lessons/1-22/add.py，打一百、-35、120 試試看。
from money import to_yuan

while True:
    text = input("金額：")
    amount = to_yuan(text)
    print("記下", amount, "元")
    break
