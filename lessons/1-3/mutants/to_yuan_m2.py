# 1-3 第③圈：壞版本 2（課程準備的）
def to_yuan(text):
    text = text.strip()
    if text.isdigit():
        return int(text)
    text = text.replace(",", "")
    text = text.replace("元", "")
    return float(text)             # 其他的寫法，先用小數轉，比較保險
