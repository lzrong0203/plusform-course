# 1-3 第③圈：壞版本 1（課程準備的）
def to_yuan(text):
    if text.isdigit():
        return text                # 本來就全是數字，就直接交回去
    text = text.replace(",", "")
    text = text.replace("元", "")
    return int(text)
