# 壞版本 m2：把 NULL 當成 0（IFNULL），金額空白的醫療多出一列 0
def category_totals(con, month):
    """查某個月（例如 "2026-11"）各分類的合計，交回 {分類: 合計}。"""
    sql = """
        SELECT category, SUM(IFNULL(amount, 0))
        FROM entries
        WHERE date LIKE ?
        GROUP BY category
    """
    totals = {}
    for category, total in con.execute(sql, (month + "%",)):
        totals[category] = total
    return totals
