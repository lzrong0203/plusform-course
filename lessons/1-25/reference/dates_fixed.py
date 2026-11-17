# 1-25 第③圈：課程的修正版（起點檔一模一樣，學員不改）。
import calendar


def next_month(d):
    # 下一個月；那個月沒有這一天，就用那個月的最後一天
    year, month = d.year, d.month + 1
    if month == 13:
        year, month = year + 1, 1
    last = calendar.monthrange(year, month)[1]
    return d.replace(year=year, month=month, day=min(d.day, last))
