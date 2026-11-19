# 壞版本 m3：零頭整個給第一個人
def split(total, people):
    if people < 1:
        raise ValueError(f"人數至少要 1 個人：{people}")
    each = total // people
    shares = []
    for i in range(people):
        shares.append(each)
    shares[0] = shares[0] + total % people
    return shares
