# 1-22 第③圈：AI 寫錯的版本 2（範例示意）：負數丟的是 TypeError，不是 ValueError。
def to_yuan(text):
    text = text.replace(",", "")
    text = text.replace("元", "")
    amount = int(text)
    if amount < 0:
        raise TypeError(f"金額不能是負數：{text}")
    return amount
