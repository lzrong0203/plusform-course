# 2-1 壞版本 m2（課程準備）：對齊了，可是少了千分位逗號
entries = [
    ("11/01", "早餐", "餐飲", 65),
    ("11/03", "午餐", "餐飲", 120),
    ("11/04", "公車", "交通", 15),
    ("11/08", "電影", "娛樂", 280),
    ("11/12", "聚餐", "餐飲", 1065),
    ("11/15", "火車", "交通", 305),
    ("11/20", "展覽", "娛樂", 200),
    ("11/22", "文具", "其他", 95),
]

totals = {}
for date, item, category, amount in entries:
    totals[category] = totals.get(category, 0) + amount

print("11 月月報")
for category, amount in totals.items():
    print(f"{category}  {amount:>5} 元")
print(f"合計  {sum(totals.values()):>5} 元")
