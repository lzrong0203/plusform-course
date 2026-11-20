# check 用（學員不用看）：另一份沒看過的帳（12 月、退款在另一類、整類金額空白、備註有單引號、隔年的帳），呼叫學員的 category_totals
import sqlite3

from db_report import category_totals

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE entries (date TEXT, item TEXT, category TEXT, amount INTEGER, note TEXT)")
rows = [("2026-11-30", "便當店", "餐飲", 95, ""), ("2026-12-01", "早餐店", "餐飲", 60, ""), ("2026-12-02", "超市", "日用品", 1200, ""),
        ("2026-12-05", "超市退款", "日用品", -300, "退貨"), ("2026-12-07", "健身房", "運動", None, "等發票"),
        ("2026-12-09", "電影院", "娛樂", 280, "Amy's 生日"), ("2027-01-02", "捷運加值", "交通", 500, "")]
con.executemany("INSERT INTO entries VALUES (?, ?, ?, ?, ?)", rows)
totals = category_totals(con, "2026-12")
for name in sorted(totals):
    print(name, totals[name])
