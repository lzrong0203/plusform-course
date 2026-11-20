# check 用（學員不用看）：建一個只在記憶體裡的資料庫（entries.csv 的 11 筆），跑學員的 SQL 檔，
#   查到的每一列排好順序印出來（欄位名稱、列的順序不管，欄位的順序要照題目）
import sqlite3
from pathlib import Path

from ledger_db import load_csv


def run(name):
    here = Path(__file__).parent
    con = sqlite3.connect(":memory:")
    load_csv(con, here / "entries.csv")
    sql = (here / name).read_text(encoding="utf-8-sig")
    body = "\n".join(ln for ln in sql.splitlines() if not ln.strip().startswith("--")).strip()
    if not body:
        print("（還沒寫 SQL）")
        return
    rows = con.execute(body).fetchall()
    for row in sorted(rows, key=str):
        print(" | ".join(str(v) for v in row).rstrip())
