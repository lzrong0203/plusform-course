# 壞版本 m3：大於等於，比較後面的月份也算進來（12 月的帳算進 11 月）
def monthly_total(entries, month):
    total = 0
    for date, item, category, amount in entries:
        if int(date.split("/")[0]) >= month:
            total += amount
    return total
