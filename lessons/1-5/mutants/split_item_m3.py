# 1-5 第③圈：壞版本 3（課程準備的）
def split_item(text):
    parts = text.split()
    item = parts[0]
    amount = int(parts[-1][:-1])                 # 把最後一個字「元」切掉
    return item, amount
