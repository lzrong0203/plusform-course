# 壞版本 m1（= 課程凍結的 AI 版本）：想跳過金額空白的，寫了 amount > 0，退票（負的）也被跳過
def category_totals(con, month):
    """查某個月（例如 "2026-11"）各分類的合計，交回 {分類: 合計}。"""
    sql = """
        SELECT category, SUM(amount)
        FROM entries
        WHERE date LIKE ? AND amount > 0   -- 金額空白的跳過
        GROUP BY category
    """
    totals = {}
    for category, total in con.execute(sql, (month + "%",)):
        totals[category] = total
    return totals
