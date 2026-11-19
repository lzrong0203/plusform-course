# 壞版本 m1：零頭沒有分出去
def split(total, people):
    if people < 1:
        raise ValueError(f"人數至少要 1 個人：{people}")
    each = total // people
    shares = []
    for i in range(people):
        shares.append(each)
    return shares
