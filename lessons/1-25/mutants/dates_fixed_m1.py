def next_month(d):
    # 沒有這一天，就跳到再下一個月的 1 號
    try:
        return d.replace(month=d.month + 1)
    except ValueError:
        return d.replace(month=d.month + 2, day=1)
