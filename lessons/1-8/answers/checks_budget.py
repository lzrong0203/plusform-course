# 1-8 第③圈的參考答案（老師端也用它驗證壞版本）
from budget import over_budget

assert over_budget(1200, 1000) == True
assert over_budget(800, 1000) == False
assert over_budget(1000, 1000) == False
assert over_budget(1001, 1000) == True
assert over_budget(0, 1000) == False
