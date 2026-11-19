# 2-3 第①圈：熊把 1-4 的分帳改成「幾個人都能分」（還沒寫完：零頭還沒放進去）
def split(total, people):
    """一筆錢 people 個人分，交回每個人各付多少（list）。

    規則（1-4 的需求卡）：先用 // 算每人付多少；零頭從第一個人開始，一人多 1 元。
    例子：split(100, 3) 是 [34, 33, 33]
    """
    each = total // people
    shares = []
    for i in range(people):
        shares.append(each)
    return shares
