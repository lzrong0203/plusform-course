# 1-19 第③圈的參考答案（影片裡熊寫的三條；老師端也用它驗證壞版本）
from over_limit import over_limit

# 沒給 limit：用 300
assert over_limit([120, 450, 85]) == [450]
# 用關鍵字給 limit
assert over_limit([120, 450, 85], limit=100) == [120, 450]
# 都沒超過：交回空的 list
assert over_limit([50, 80]) == []
