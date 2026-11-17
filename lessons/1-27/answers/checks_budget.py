# 1-27 第三部分：老師的標準檢查（參考答案；寫法不只一種）
from budget_ai import set_budget

b = {}
assert set_budget(b, "2026-11", "8,000元") == 8000
assert b == {"2026-11": 8000}                       # 存進去的是整數 8000（抓壞版本 3）
assert set_budget(b, "2026-11", "6000") == 6000     # 同一個月再設一次
assert b == {"2026-11": 6000}                       # 蓋掉舊的
assert set_budget(b, "2026-12", "1") == 1           # 1 元可以

try:
    set_budget(b, "2026-12", "0")                   # 0 元不行（抓壞版本 1）
except ValueError:
    pass
else:
    assert False, "0 元應該丟 ValueError"

try:
    set_budget(b, "2026-13", "100")                 # 沒有 13 月（抓壞版本 2）
except ValueError:
    pass
else:
    assert False, "2026-13 應該丟 ValueError"

assert b == {"2026-11": 6000, "2026-12": 1}         # 不合法的兩次，都沒有改到 budgets
