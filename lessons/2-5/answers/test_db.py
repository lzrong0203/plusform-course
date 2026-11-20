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


def test_totals():
    totals = category_totals(make_db(), "2026-11")
    assert totals == {"餐飲": 635, "交通": 500, "日用品": 680, "娛樂": 320}
