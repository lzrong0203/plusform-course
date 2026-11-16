# 1-22 第③圈：AI 寫錯的版本 1（範例示意）：看不懂的金額用光禿禿的 except 吞掉，當成 0。
def to_yuan(text):
    text = text.replace(",", "")
    text = text.replace("元", "")
    try:
        amount = int(text)
    except:
        return 0
    if amount < 0:
        raise ValueError(f"金額不能是負數：{text}")
    return amount
