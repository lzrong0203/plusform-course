# 壞版本 m2：沒打日期的時候，沒有換成今天（交回空的字串）
from datetime import date


def today():
    """今天的日期。另外寫成一個函式，測試的時候才換得掉。"""
    return date.today()


def fill_date(text):
    """日期沒打（直接按 Enter），就用今天，寫成 11/03 這種樣子；有打就照用。"""
    return text
