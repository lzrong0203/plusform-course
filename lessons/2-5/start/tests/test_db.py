# 2-5 第③圈：驗收測試（先寫好，再把 db_report.py 交給 AI 寫）
import sqlite3
from pathlib import Path

from db_report import category_totals
from ledger_db import load_csv

FOLDER = Path(__file__).parent.parent   # tests 的上一層，就是 lessons/2-5


def make_db():
    con = sqlite3.connect(":memory:")   # 只在記憶體裡、用完就丟的資料庫
    load_csv(con, FOLDER / "entries.csv")
    return con


def test_count():
    con = make_db()
    assert con.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 11


# 換你寫：test_totals。11 月各分類的合計，要跟 CSV 版一樣
#   自己照 entries.csv 手算（退票要扣掉、金額空白的不算）
