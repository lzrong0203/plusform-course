# 1-22 第③圈：AI 寫錯的版本 3（範例示意）：負數有丟 ValueError，訊息裡卻沒有那個值。
def to_yuan(text):
    text = text.replace(",", "")
    text = text.replace("元", "")
    amount = int(text)
    if amount < 0:
        raise ValueError("金額不能是負數")
    return amount
