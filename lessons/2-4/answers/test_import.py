# 2-4 第③圈：驗收測試（先寫好，再把 import_bank.py 交給 AI 寫）
import json
from pathlib import Path

from import_bank import category_totals, import_statement

FOLDER = Path(__file__).parent.parent   # tests 的上一層，就是 lessons/2-4
KEYWORDS = json.loads((FOLDER / "settings.json").read_text(encoding="utf-8"))["分類關鍵字"]


def test_count():
    entries = import_statement(FOLDER / "bank_a.csv", KEYWORDS)
    assert len(entries) == 6   # 空白列不算，一共 6 筆


def test_first_entry():
    entries = import_statement(FOLDER / "bank_a.csv", KEYWORDS)
    assert entries[0] == ("2026/11/01", "早餐店", "餐飲", 65)


def test_totals():
    entries = import_statement(FOLDER / "bank_a.csv", KEYWORDS)
    assert category_totals(entries) == {"餐飲": 185, "交通": 500, "日用品": 900, "娛樂": 320}
