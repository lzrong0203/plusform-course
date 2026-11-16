# 1-20 第①圈的正確版：依金額、再依日期（先照日期排一次，再照金額排一次；穩定排序讓金額一樣的留著日期的順序）。

entries = [("11/03", "餐", 120), ("11/01", "車", 85), ("11/02", "書", 120), ("11/04", "餐", 85)]

by_date = sorted(entries, key=lambda e: e[0])
result = sorted(by_date, key=lambda e: e[2])

for date, cat, amount in result:
    print(date, cat, amount)
