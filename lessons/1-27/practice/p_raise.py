# 矯正包練習：不要把錯吞掉：讓錯丟出去，在外面只接 ValueError（1-22）
# 照下面改：
#   1. to_yuan 裡拿掉 try／except：int 看不懂就讓 ValueError 丟出去；負數時 raise ValueError，訊息裡放進那個值。
#   2. 迴圈裡用 try 包住加總那一行，except ValueError as e: 印出「看不懂：」和 e；看得懂的照常加。
# 改好在帳本資料夾打 uv run lessons/1-27/practice/p_raise.py，要印出：
#   看不懂： invalid literal for int() with base 10: '兩百'
#   看不懂： 金額不能是負數：-20
#   合計 345
# 再把 int(text) 故意打錯成 int(txet) 跑一次：要看得到 NameError（打錯字沒有被藏起來），看完改回來。


def to_yuan(text):
    try:
        amount = int(text)
        if amount < 0:
            return 0
        return amount
    except:
        return 0


total = 0
for t in ["300", "兩百", "-20", "45"]:
    total = total + to_yuan(t)
print("合計", total)
