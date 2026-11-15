# 1-13 第③圈的參考答案（老師端也用它驗證壞版本）
from entries import remove_last, index_of_max

# 刪掉最後一筆：交回那一筆，list 少一筆
a = [120, 85, 200]
assert remove_last(a) == 200
assert a == [120, 85]
# 最大的一筆在第幾個位置（從 0 數）
b = [120, 300, 85]
assert index_of_max(b) == 1
# 查的時候不能動到原本的順序
assert b == [120, 300, 85]
# 一樣大的，交回前面那一筆
assert index_of_max([300, 85, 300]) == 0
