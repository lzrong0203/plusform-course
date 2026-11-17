import calendar


def next_month(d):
    # 一律用下個月的最後一天，就不會超過
    year, month = d.year, d.month + 1
    if month == 13:
        year, month = year + 1, 1
    last = calendar.monthrange(year, month)[1]
    return d.replace(year=year, month=month, day=last)
