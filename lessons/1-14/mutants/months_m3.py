# 1-14 壞版本 3


def both_months(nov, dec):
    both = []
    for kind in nov:
        if kind in dec:
            both.append(kind)
    return sorted(both)
