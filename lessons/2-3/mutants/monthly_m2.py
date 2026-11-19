# 壞版本 m2：沒有挑月份，每個月的帳全部加起來
def monthly_total(entries, month):
    total = 0
    for date, item, category, amount in entries:
        total += amount
    return total
