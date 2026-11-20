# 2-5 第③圈：查某個月各分類的合計（正確版）
def category_totals(con, month):
    """查某個月（例如 "2026-11"）各分類的合計，交回 {分類: 合計}；金額空白的不算，退票（負的）要扣掉。"""
    sql = """
        SELECT category, SUM(amount)
        FROM entries
        WHERE date LIKE ? AND amount IS NOT NULL
        GROUP BY category
    """
    totals = {}
    for category, total in con.execute(sql, (month + "%",)):
        totals[category] = total
    return totals
