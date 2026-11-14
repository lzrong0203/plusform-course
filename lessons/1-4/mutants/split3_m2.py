# 1-4 第③圈：壞版本 2（課程準備的）
def split3(total):
    each = total // 3
    left = total % 3
    return each + left, each, each     # 零頭全部給第一個人
