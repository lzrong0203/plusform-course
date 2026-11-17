# 1-25 第③圈：report.py（正確版）：第 4 行改成從課程的修正版 dates_fixed 拿 next_month。
from datetime import date
import settings
from card import use_card
from dates_fixed import next_month

use_card()
d = date(2026, 1, settings.PAY_DAY)
print("這期扣款", d)
print("下期扣款", next_month(d))
