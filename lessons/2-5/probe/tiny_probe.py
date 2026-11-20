# check 用（學員不用看）：跑學員的 tiny.sql（自己建的小表 t），看放了幾筆、有沒有一筆金額是空的
import sqlite3
from pathlib import Path

con = sqlite3.connect(":memory:")
con.executescript((Path(__file__).parent / "tiny.sql").read_text(encoding="utf-8-sig"))
print("一共", con.execute("SELECT COUNT(*) FROM t").fetchone()[0], "筆")
print("金額空白的", con.execute("SELECT COUNT(*) FROM t WHERE amount IS NULL").fetchone()[0], "筆")
