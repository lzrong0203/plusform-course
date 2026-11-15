# 1-13 壞版本 1


def remove_last(amounts):
    return amounts.pop()


def index_of_max(amounts):
    where = 0
    for i, cost in enumerate(amounts):
        if cost > amounts[where]:
            where = i
    amounts.sort()
    return where
