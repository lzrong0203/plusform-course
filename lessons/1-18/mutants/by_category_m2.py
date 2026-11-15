# 1-18 第③圈 壞版本 2（課程準備的 AI 版本，範例示意）：同一類的金額沒有加起來，後面的蓋掉前面的


def by_category(entries):
    """各分類的小計。"""
    result = {}
    for kind, amount in entries:
        result[kind] = amount
    return result
