# 範例示意：把 db_report.py 交給 AI 寫，它交回來的樣子（課程凍結的版本，第③圈拿來驗收）
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
