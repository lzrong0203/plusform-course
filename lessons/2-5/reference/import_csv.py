# 2-5 第①圈：把 entries.csv 的帳，放進一個 SQLite 練習檔 practice.db
import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "practice.db"
DB.unlink(missing_ok=True)   # 練習用：每次跑都重做一份新的
con = sqlite3.connect(DB)
con.execute("CREATE TABLE entries (date TEXT, item TEXT, category TEXT, amount INTEGER, note TEXT)")

with open(HERE / "entries.csv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        d, item, cat, note = row["日期"], row["項目"], row["分類"], row["備註"]
        amount = int(row["金額"]) if row["金額"] else None
        con.execute("INSERT INTO entries VALUES (?, ?, ?, ?, ?)", (d, item, cat, amount, note))
con.commit()
print("一共", con.execute("SELECT COUNT(*) FROM entries").fetchone()[0], "筆")
con.close()
