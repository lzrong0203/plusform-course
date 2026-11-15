# 1-15 壞版本 2


def shares(totals):
    whole = sum(totals.values())
    result = {}
    for kind, amount in totals.items():
        result[kind] = round(amount / whole * 100)
    return result
