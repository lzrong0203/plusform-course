# 課程準備的小工具（不用改）：把一個 .sql 檔交給 practice.db 跑，印出查到的每一列
#   用法（在帳本資料夾）：uv run lessons/2-5/run_sql.py q1.sql
#   SQL 檔裡有 CREATE TABLE 的話（例如 tiny.sql），改在一個用完就丟的空資料庫跑，不動 practice.db
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main(name):
    sql = (HERE / name).read_text(encoding="utf-8-sig")
    if "CREATE TABLE" in sql.upper():
        con = sqlite3.connect(":memory:")
    elif (HERE / "practice.db").exists():
        con = sqlite3.connect(HERE / "practice.db")
    else:
        print("還沒有 practice.db：先在帳本資料夾打 uv run lessons/2-5/import_csv.py")
        return
    buf = ""
    for line in sql.splitlines(keepends=True):
        buf += line
        if sqlite3.complete_statement(buf):
            cur = con.execute(buf)
            if cur.description:
                print(" | ".join(c[0] for c in cur.description))
                for row in cur.fetchall():
                    print(" | ".join(str(v) for v in row))
            buf = ""
    con.close()


main(sys.argv[1] if len(sys.argv) > 1 else "q1.sql")
