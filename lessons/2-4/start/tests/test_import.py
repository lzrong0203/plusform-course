# 2-4 第③圈：驗收測試（先寫好，再把 import_bank.py 交給 AI 寫）
import json
from pathlib import Path

from import_bank import category_totals, import_statement

FOLDER = Path(__file__).parent.parent   # tests 的上一層，就是 lessons/2-4
KEYWORDS = json.loads((FOLDER / "settings.json").read_text(encoding="utf-8"))["分類關鍵字"]


def test_count():
    entries = import_statement(FOLDER / "bank_a.csv", KEYWORDS)
    assert len(entries) == 6   # 空白列不算，一共 6 筆


# 換你寫：test_totals。匯入 bank_a.csv 以後，各分類的合計應該是多少？
#   自己照 bank_a.csv 手算（退款是負的，要扣掉），寫成 assert totals == {"餐飲": …, …}
