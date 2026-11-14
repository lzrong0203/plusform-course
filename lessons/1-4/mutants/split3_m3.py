# 1-4 第③圈：壞版本 3（課程準備的）
def split3(total):
    each = int(total / 3)              # 先除，再把小數點後面去掉
    left = total % 3
    first = each + (left + 1) // 2
    second = each + left // 2
    third = each
    return first, second, third
