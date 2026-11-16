# 1-21 第①圈：main.py（正確版）。跟 money.py 放在同一個資料夾。
from datetime import date, datetime
from money import fmt, total

amounts = [120, 450, 1250]
print("合計", fmt(total(amounts)))
print("本月", date.today().strftime("%Y-%m"))
d = datetime.strptime("2026-11-03", "%Y-%m-%d")
print(d.month, d.day)
