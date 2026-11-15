# 1-18 第③圈的凍結版：影片裡 AI（Claude 網頁版的一般聊天，示範帳號，2026-11-15）照同一份 docstring 和 assert 寫的函式，原樣保存、之後不再改。
# 沒有 AI 帳號的同學：把 docstring 下面的函式內容（totals = {} 到 return totals），抄進你帳本的 lessons/1-18/by_category.py（docstring 留你自己寫的）。
# totals[category] += amount 的意思是「把 amount 加上去，再放回 totals[category]」，跟 totals[category] = totals[category] + amount 一樣。


def by_category(entries):
    """各分類的小計。

    輸入：entries 是一串 (分類, 金額)，可以是空的。
    輸出：dict，分類 → 那一類的合計金額；空的 list 交回 {}。
    例子：by_category([("餐", 120), ("車", 30), ("餐", 85)]) 是 {"餐": 205, "車": 30}
    """
    totals = {}
    for category, amount in entries:
        if category in totals:
            totals[category] += amount
        else:
            totals[category] = amount
    return totals
