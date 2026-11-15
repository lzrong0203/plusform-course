# 1-18 第③圈的參考答案（老師端也用它驗證壞版本）
from by_category import by_category

# 同一類的兩筆要加起來
assert by_category([("餐", 120), ("餐", 85)]) == {"餐": 205}
# 兩類各自加
assert by_category([("餐", 120), ("車", 30), ("餐", 85)]) == {"餐": 205, "車": 30}
# 空的 list：交回空的 dict
assert by_category([]) == {}
