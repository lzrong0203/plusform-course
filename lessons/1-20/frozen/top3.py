# 1-20 第③圈的凍結版：影片裡示範帳號的聊天版 AI 照熊的型別提示、docstring 和 assert 寫的函式（2026-11-16 實錄，原樣）。
# 沒有 AI 帳號的，把 docstring 下面的函式內容（totals: dict[str, int] = {} 到 return 那一行）抄進自己的 top3.py。


def top3(entries: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """依分類加總，排出花費最大的前三類。

    輸入：entries，一串 (分類, 金額)，同一類可以有好幾筆
    輸出：list，每一筆是 (分類, 合計)，合計大的在前，最多三類
          entries 是空的，交回 []
    例子：top3([("餐", 120), ("書", 450), ("餐", 300)])
          是 [("書", 450), ("餐", 420)]
    """
    totals: dict[str, int] = {}
    for category, amount in entries:
        totals[category] = totals.get(category, 0) + amount
    return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:3]
