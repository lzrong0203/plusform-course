# 壞版本 m4：一筆都沒有的時候，交回 None（不是 0）
def monthly_total(entries, month):
    amounts = [amount for date, item, category, amount in entries if int(date.split("/")[0]) == month]
    if amounts:
        return sum(amounts)
