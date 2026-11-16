# 1-21 第①圈：main.py。下面的 total、fmt 是熊的金額工具，以前每個檔都複製一份。
# 1. 把 total、fmt 搬到旁邊的 money.py（剪下、貼過去），這裡改成一行 from money import fmt, total
# 2. 本月：把第一個 "…" 換成格式碼，印出今天的年和月（例如 2026-11）
# 3. 把第二個 "…" 換成格式碼，用 datetime.strptime 把 "2026-11-03" 解析成日期，印出 11 3
#    格式碼查官方文件：https://docs.python.org/3.13/library/datetime.html#format-codes
# 寫完在帳本資料夾打：uv run lessons/1-21/main.py
from datetime import date, datetime


def total(amounts):
    return sum(amounts)


def fmt(amount):
    return f"{amount:,} 元"


amounts = [120, 450, 1250]
print("合計", fmt(total(amounts)))
print("本月", date.today().strftime("…"))
d = datetime.strptime("2026-11-03", "…")
print(d.month, d.day)
