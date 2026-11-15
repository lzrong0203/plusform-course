# 1-14 第③圈的參考答案（老師端也用它驗證壞版本）
from months import both_months

nov = ["餐飲", "交通", "餐飲", "娛樂"]
dec = ["交通", "醫療", "餐飲", "交通"]
# 兩個月都有的分類，每個只出現一次，排好序（比整串，連順序一起比）
assert both_months(nov, dec) == ["交通", "餐飲"]
# 只有一個月有的，不能放進去
assert "娛樂" not in both_months(nov, dec)
assert "醫療" not in both_months(nov, dec)
# 同一個分類記了好幾筆，也只算一次
assert both_months(["餐飲", "餐飲"], ["餐飲"]) == ["餐飲"]
# 兩個月沒有一樣的分類，交回空的 list
assert both_months(["娛樂"], ["醫療"]) == []
