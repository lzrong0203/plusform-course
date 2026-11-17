from datetime import date
import settings
from card import use_card
from dates import next_month

use_card()
d = date(2026, 1, settings.PAY_DAY)
print("這期扣款", d)
print("下期扣款", next_month(d))
