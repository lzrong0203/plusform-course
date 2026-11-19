# 2-3 第①圈：fill_date("") 會用今天的日期。用 monkeypatch 把「今天」換成固定的一天，這個測試才不會明天就不過
import dates
from datetime import date


# 換你寫兩個測試：
#   def test_typed_date_kept():  有打日期（例如 "10/31"），fill_date 照用
#   def test_empty_means_today(monkeypatch):
#       第一行用 monkeypatch.setattr(dates, "today", lambda: date(年, 月, 日)) 把今天換成固定的一天
#       第二行 assert dates.fill_date("") 是那一天（寫成 月/日，兩位數）
