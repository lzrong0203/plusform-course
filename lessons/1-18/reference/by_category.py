# 1-18 第③圈：各分類的小計（正確版）


def by_category(entries):
    """各分類的小計。

    輸入：entries 是一串 (分類, 金額)，可以是空的。
    輸出：dict，分類 → 那一類的合計金額；空的 list 交回 {}。
    例子：by_category([("餐", 120), ("車", 30), ("餐", 85)]) 是 {"餐": 205, "車": 30}
    """
    result = {}
    for kind, amount in entries:
        result[kind] = result.get(kind, 0) + amount
    return result
