# 壞版本 z1：沒有先檢查人數，人數是 0 的時候除以 0（ZeroDivisionError，不是 ValueError）
def split(total, people):
    each = total // people
    shares = []
    for i in range(people):
        shares.append(each)
    for i in range(total % people):
        shares[i] = shares[i] + 1
    return shares
