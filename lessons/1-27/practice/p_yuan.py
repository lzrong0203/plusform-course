# 矯正包練習：把金額文字變成整數，不合法就丟出 ValueError（1-5 的 replace、1-22 的 raise）
# 寫好 to_yuan：拿掉逗號和「元」，用 int() 變成整數；小於或等於 0 就 raise ValueError，訊息裡放進 text。
# 寫好在帳本資料夾打 uv run lessons/1-27/practice/p_yuan.py，要印出：1200 35，接著兩行「丟出 ValueError」
def to_yuan(text):
    """把 "1,200元" 這種金額變成整數；不合法丟出 ValueError。"""


print(to_yuan("1,200元"), to_yuan("35"))
for bad in ["0", "八十"]:
    try:
        to_yuan(bad)
        print(bad, "沒有丟出錯誤")
    except ValueError:
        print(bad, "丟出 ValueError")
