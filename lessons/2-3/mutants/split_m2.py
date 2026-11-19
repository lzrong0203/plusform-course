# 壞版本 m2：零頭從最後一個人開始加
def split(total, people):
    if people < 1:
        raise ValueError(f"人數至少要 1 個人：{people}")
    each = total // people
    shares = []
    for i in range(people):
        shares.append(each)
    for i in range(total % people):
        shares[people - 1 - i] = shares[people - 1 - i] + 1
    return shares
