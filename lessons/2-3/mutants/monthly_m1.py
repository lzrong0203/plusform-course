# 壞版本 m1：用「開頭是不是」比月份，1 月會算到 10、11、12 月去（01/05 反而不算）
def monthly_total(entries, month):
    total = 0
    for date, item, category, amount in entries:
        if date.startswith(str(month)):
            total += amount
    return total
