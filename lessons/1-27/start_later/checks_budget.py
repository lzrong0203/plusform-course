# 1-27 第三部分（2）：用 assert 驗收 AI 交回來的 set_budget
# budget_ai.py 是 AI 照需求交回來的版本（課程準備的固定版本，範例示意，不要改它）。
# 寫完在帳本資料夾打 uv run lessons/1-27/checks_budget.py：跳出 AssertionError，就是抓到它不符合需求的地方。
from budget_ai import set_budget

b = {}
assert set_budget(b, "2026-11", "8,000元") == 8000    # 範例：交回設定好的金額

# 換你寫：至少再四條。一條規則想一條：月在 01 到 12、金額要大於 0、存進 budgets 的是什麼、同一個月再設一次……
# 「應該丟出 ValueError」照 1-22 的寫法用 try 寫：
#   try:
#       set_budget(b, ……)
#   except ValueError:
#       pass
#   else:
#       assert False, "……應該丟 ValueError"
