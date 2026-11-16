# 1-22 第③圈：老師的標準檢查（跟影片裡熊寫的三條一樣）
from money import to_yuan

# 一般的金額：拿掉逗號和元，變成整數
assert to_yuan("1,200元") == 1200
# 看不懂的金額：要丟 ValueError，訊息裡要有那段字
try:
    to_yuan("一百")
except ValueError as e:
    assert "一百" in str(e)
else:
    assert False
# 負數：要丟 ValueError，訊息裡要有那個值
try:
    to_yuan("-35")
except ValueError as e:
    assert "-35" in str(e)
else:
    assert False
