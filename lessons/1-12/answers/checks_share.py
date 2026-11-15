# Lv1 上關卡　第三部分的參考答案（老師端也用它驗證壞版本）
from share import share

assert share(900, 3, 1) == 300
assert share(1000, 3, 1) == 334
assert share(1000, 3, 2) == 333
assert share(1001, 3, 2) == 334
assert share(1000, 4, 1) == 250
assert share(1001, 3, 1) + share(1001, 3, 2) + share(1001, 3, 3) == 1001
