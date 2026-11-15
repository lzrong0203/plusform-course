# 1-15 壞版本 3


def shares(totals):
    whole = sum(totals.values())
    result = {}
    for kind, amount in totals.items():
        if amount > 0:
            result[kind] = round(amount / whole * 100, 1)
    return result
