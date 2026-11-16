def top3(entries: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """依分類加總，排出花費最大的前三類。

    輸入：entries，一串 (分類, 金額)，同一類可以有好幾筆
    輸出：list，每一筆是 (分類, 合計)，合計大的在前，最多三類
          entries 是空的，交回 []
    例子：top3([("餐", 120), ("書", 450), ("餐", 300)])
          是 [("書", 450), ("餐", 420)]
    """
    return sorted(entries, key=lambda e: e[1], reverse=True)[:3]
