import calendar


def next_month(d):
    # 下一個月；那個月沒有這一天，就用那個月的最後一天
    last = calendar.monthrange(d.year, d.month + 1)[1]
    return d.replace(month=d.month + 1, day=min(d.day, last))
