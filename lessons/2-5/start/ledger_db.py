# 課程準備（不用改）：把 entries.csv 放進資料表 entries。第①圈 import_csv.py 的寫法，包成函式給測試用
import csv


def load_csv(con, csv_path):
    con.execute("CREATE TABLE entries (date TEXT, item TEXT, category TEXT, amount INTEGER, note TEXT)")
    with open(csv_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            amount = int(row["金額"]) if row["金額"] else None
            con.execute("INSERT INTO entries VALUES (?, ?, ?, ?, ?)", (row["日期"], row["項目"], row["分類"], amount, row["備註"]))
    con.commit()
