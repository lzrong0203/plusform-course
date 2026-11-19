# 2-3 參考答案（老師的標準測試）：期望值自己手算；帳裡要有別的月份、要有 1 月；一筆都沒有是 0
from monthly import monthly_total

ENTRIES = [
    ("01/05", "早餐", "餐飲", 60),
    ("10/31", "晚餐", "餐飲", 150),
    ("11/03", "午餐", "餐飲", 120),
    ("11/04", "公車", "交通", 15),
    ("12/01", "電影", "娛樂", 280),
]


def test_november():
    assert monthly_total(ENTRIES, 11) == 135


def test_january():
    assert monthly_total(ENTRIES, 1) == 60


def test_no_entries():
    assert monthly_total([], 11) == 0
