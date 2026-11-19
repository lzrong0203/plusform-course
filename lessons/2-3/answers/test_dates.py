# 2-3 參考答案（老師的標準測試）：用 monkeypatch 把「今天」換成 2026 年 11 月 3 日
import dates
from datetime import date


def test_typed_date_kept():
    assert dates.fill_date("10/31") == "10/31"


def test_empty_means_today(monkeypatch):
    monkeypatch.setattr(dates, "today", lambda: date(2026, 11, 3))
    assert dates.fill_date("") == "11/03"
