# 1-18 第③圈 壞版本 3（課程準備的 AI 版本，範例示意）：空的 list 直接 return，交回的是 None，不是 {}


def by_category(entries):
    """各分類的小計。"""
    if len(entries) == 0:
        return
    result = {}
    for kind, amount in entries:
        result[kind] = result.get(kind, 0) + amount
    return result
