# 2-4 第①圈：用 csv 模組把帳存成 ledger.csv（備註有逗號也不怕）
import csv
from pathlib import Path

FIELDS = ["日期", "項目", "金額", "備註"]
entries = [
    {"日期": "11/03", "項目": "午餐", "金額": 120, "備註": "跟同事"},
    {"日期": "11/04", "項目": "公車", "金額": 15, "備註": ""},
    {"日期": "11/05", "項目": "聚餐", "金額": 600, "備註": "跟小明, 小華"},
]
p = Path(__file__).parent / "ledger.csv"
# 換你寫：with open 打開 p（"w"、encoding="utf-8"、newline=""），
#   用 csv.DictWriter 先寫標題列（writeheader），再寫每一筆（writerows）

print("存好了")
