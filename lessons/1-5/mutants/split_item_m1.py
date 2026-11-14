# 1-5 第③圈：壞版本 1（課程準備的）
def split_item(text):
    parts = text.strip().split(" ")              # 用一個半形空白來拆
    item = parts[0]
    amount = int(parts[-1].replace("元", ""))
    return item, amount
