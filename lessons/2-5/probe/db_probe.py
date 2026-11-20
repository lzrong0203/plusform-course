# check 用（學員不用看）：import_csv.py 跑完以後，看 practice.db 裡存了什麼
import sqlite3
from pathlib import Path

con = sqlite3.connect(Path(__file__).parent / "practice.db")
cols = [r[1] for r in con.execute("PRAGMA table_info(entries)")]
print("欄位", " ".join(cols))
print("一共", con.execute("SELECT COUNT(*) FROM entries").fetchone()[0], "筆")
for item, amount, note in con.execute("SELECT item, amount, note FROM entries WHERE item IN ('麵包店', '牙醫') ORDER BY date"):
    print(item, amount, note)
