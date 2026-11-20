# 壞版本 m3：沒有篩月份，10 月的帳也加進去
def category_totals(con, month):
    """查某個月（例如 "2026-11"）各分類的合計，交回 {分類: 合計}。"""
    sql = """
        SELECT category, SUM(amount)
        FROM entries
        WHERE amount IS NOT NULL
        GROUP BY category
    """
    totals = {}
    for category, total in con.execute(sql):
        totals[category] = total
    return totals
