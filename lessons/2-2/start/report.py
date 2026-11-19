# 2-2 熊的 11 月月報：這個月多了「日用品」這一類，對齊又歪了（這一課要請 AI 改成表格）
entries = [
    ("11/01", "早餐", "餐飲", 65),
    ("11/03", "午餐", "餐飲", 120),
    ("11/04", "公車", "交通", 15),
    ("11/06", "衛生紙", "日用品", 189),
    ("11/08", "電影", "娛樂", 280),
    ("11/12", "聚餐", "餐飲", 1065),
    ("11/15", "火車", "交通", 305),
    ("11/18", "洗衣精", "日用品", 259),
    ("11/20", "展覽", "娛樂", 200),
    ("11/22", "文具", "其他", 95),
]

totals = {}
for date, item, category, amount in entries:
    totals[category] = totals.get(category, 0) + amount

print("11 月月報")
for category, amount in totals.items():
    print(f"{category}  {amount:>5,} 元")
print(f"合計  {sum(totals.values()):>5,} 元")
