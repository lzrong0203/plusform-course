# 壞版本 m3：沒有補零（11/03 變成 11/3）
from datetime import date


def today():
    """今天的日期。另外寫成一個函式，測試的時候才換得掉。"""
    return date.today()


def fill_date(text):
    """日期沒打（直接按 Enter），就用今天，寫成 11/03 這種樣子；有打就照用。"""
    if text == "":
        d = today()
        return f"{d.month}/{d.day}"
    return text
