# 1-5 第③圈：壞版本 2（課程準備的）
def split_item(text):
    parts = text.strip().split(" ")
    item = parts[0]
    amount = int(parts[1].replace("元", ""))    # 第二段就是金額
    return item, amount
