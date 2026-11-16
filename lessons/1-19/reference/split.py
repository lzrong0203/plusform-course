# 1-19 第①圈：split.py 的正確版（report_long.py 拆成五個小函式）


def total(entries):
    """合計。輸入：一串 (分類, 金額)。輸出：金額加起來。"""
    s = 0
    for kind, amount in entries:
        s = s + amount
    return s


def by_category(entries):
    """各分類的小計。輸入：一串 (分類, 金額)。輸出：dict，分類 → 合計。"""
    cats = {}
    for kind, amount in entries:
        cats[kind] = cats.get(kind, 0) + amount
    return cats


def biggest(entries):
    """最大的一筆。輸入：一串 (分類, 金額)，至少一筆。輸出：金額最大的那一筆 (分類, 金額)。"""
    big = entries[0]
    for entry in entries:
        if entry[1] > big[1]:
            big = entry
    return big


def light(s, budget=1000):
    """預算燈號（1-9）。輸入：合計 s、預算 budget（沒給就是 1000）。輸出："綠燈"、"黃燈" 或 "紅燈"。"""
    ratio = s / budget
    if ratio < 0.8:
        return "綠燈"
    elif ratio <= 1:
        return "黃燈"
    else:
        return "紅燈"


def report(entries, budget=1000):
    """印出一個月的報表，用上面四個函式。輸入：一串 (分類, 金額)、預算 budget（沒給就是 1000）。不交回東西。"""
    print("== 11 月報表（預算", budget, "元）==")
    s = total(entries)
    print("合計", s, "元")
    cats = by_category(entries)
    for kind in cats:
        print(" ", kind, cats[kind], "元")
    big = biggest(entries)
    print("最大的一筆", big[0], big[1], "元")
    print(light(s, budget))


nov = [("餐", 120), ("車", 30), ("餐", 85), ("書", 450), ("車", 60), ("餐", 300)]
report(nov)
report(nov, budget=1200)
