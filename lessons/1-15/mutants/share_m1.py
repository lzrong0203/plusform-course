# 1-15 壞版本 1


def shares(totals):
    whole = sum(totals.values())
    for kind, amount in totals.items():
        totals[kind] = round(amount / whole * 100, 1)
    return totals
