# 範例示意：請 AI 幫 monthly_total 寫測試，它交回來的樣子（課程凍結的版本，第③圈拿來審）
from monthly import monthly_total

ENTRIES = [
    ("11/01", "早餐", "餐飲", 65),
    ("11/03", "午餐", "餐飲", 120),
    ("11/04", "公車", "交通", 15),
]


def test_not_negative():
    assert monthly_total(ENTRIES, 11) >= 0


def test_same_as_sum():
    expected = 0
    for date, item, category, amount in ENTRIES:
        if int(date.split("/")[0]) == 11:
            expected += amount
    assert monthly_total(ENTRIES, 11) == expected


def test_empty():
    assert monthly_total([], 11) == 0
