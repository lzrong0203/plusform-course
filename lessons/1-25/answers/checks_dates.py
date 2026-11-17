# 1-25 第③圈（參考答案）：bug 回報的重現步驟寫成檢查，驗收課程的修正版 dates_fixed.py
from datetime import date

from dates_fixed import next_month

assert next_month(date(2026, 1, 31)) == date(2026, 2, 28)   # 回報裡的那一天
assert next_month(date(2026, 1, 15)) == date(2026, 2, 15)   # 原本就好好的日子
assert next_month(date(2026, 12, 15)) == date(2027, 1, 15)  # 年底：跨到明年
