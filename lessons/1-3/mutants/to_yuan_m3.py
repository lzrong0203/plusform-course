# 1-3 第③圈：壞版本 3（課程準備的）
def to_yuan(text):
    text = text.replace("元", "")  # 拿掉「元」
    return int(text)
