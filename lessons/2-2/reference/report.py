# 2-2 正確版（課程準備）：用 rich 的 Table 印成表格（rich 會算中文字在終端機佔兩格，日用品那一行也對得齊）
from rich.console import Console
from rich.table import Table

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

table = Table(title="11 月月報")
table.add_column("分類")
table.add_column("金額", justify="right")
for category, amount in totals.items():
    table.add_row(category, f"{amount:,} 元")
table.add_row("合計", f"{sum(totals.values()):,} 元")
Console().print(table)
