# 2-3 正確版（課程準備）：零頭從第一個人開始，一人多 1 元；人數不到 1 個人，丟出 ValueError
def split(total, people):
    """一筆錢 people 個人分，交回每個人各付多少（list）。

    規則（1-4 的需求卡）：先用 // 算每人付多少；零頭從第一個人開始，一人多 1 元。
    人數不到 1 個人，raise ValueError。
    例子：split(100, 3) 是 [34, 33, 33]
    """
    if people < 1:
        raise ValueError(f"人數至少要 1 個人：{people}")
    each = total // people
    shares = []
    for i in range(people):
        shares.append(each)
    for i in range(total % people):
        shares[i] = shares[i] + 1
    return shares
