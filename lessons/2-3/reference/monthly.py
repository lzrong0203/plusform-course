# 2-3 正確版（課程準備）：一個月花了多少
def monthly_total(entries, month):
    """entries 裡，某一個月的金額加起來。

    entries：一串 (日期, 項目, 分類, 金額)，日期寫成 11/03 這種樣子（月/日，都是兩位數）
    month：月份，整數，例如 11
    例子：monthly_total([("10/31", "晚餐", "餐飲", 150), ("11/03", "午餐", "餐飲", 120)], 11) 是 120
    一筆都沒有，就是 0
    """
    total = 0
    for date, item, category, amount in entries:
        if int(date.split("/")[0]) == month:
            total += amount
    return total
