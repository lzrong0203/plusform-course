# 1-16 第③圈：老師的標準檢查（validate 用；學員寫一條「固定開銷還是 12499」就能抓到三個壞版本）
from budget import fixed, nov, dec

# 兩個月都從固定開銷開始：前兩筆是房租和手機
assert nov[:2] == [12000, 499]
# 固定開銷本身不能被改到
assert sum(fixed) == 12499
# 11 月：固定開銷加午餐
assert sum(nov) == 12619
# 12 月：固定開銷加機票
assert sum(dec) == 15499
