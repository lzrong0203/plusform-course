# 1-22 第①圈：熊的 money.py（正確版）。1-3 的轉換機 to_yuan，加上「負數就 raise ValueError，訊息裡放進那個值」。
def to_yuan(text):
    text = text.replace(",", "")
    text = text.replace("元", "")
    amount = int(text)
    if amount < 0:
        raise ValueError(f"金額不能是負數：{text}")
    return amount


if __name__ == "__main__":
    print(to_yuan("1,200"))
    print(to_yuan("一百"))
