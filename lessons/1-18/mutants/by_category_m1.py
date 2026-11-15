# 1-18 第③圈 壞版本 1（課程準備的 AI 版本，範例示意）：算的是每一類有幾筆，不是金額加起來


def by_category(entries):
    """各分類的小計。"""
    result = {}
    for kind, amount in entries:
        result[kind] = result.get(kind, 0) + 1
    return result
