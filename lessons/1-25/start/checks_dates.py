# 1-25 第③圈：把 bug 回報的重現步驟寫成檢查，驗收課程的修正版 dates_fixed.py
# 每一條寫成：assert next_month(某一天) == 應該是哪一天（日期用 date(年, 月, 日) 寫）
# 至少寫 3 條。在帳本資料夾跑：uv run lessons/1-25/checks_dates.py
# 什麼都沒印＝每一條都成立；印出 AssertionError，就看是哪一行。
from datetime import date

from dates_fixed import next_month

