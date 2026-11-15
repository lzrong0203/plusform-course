# 1-16 第③圈：AI 寫的兩個月預算（課程準備的版本，範例示意）。它跑得起來，可是算錯了。
# 每個月都有的固定開銷 fixed：房租 12000、手機 499
# nov：11 月＝固定開銷＋午餐 120；dec：12 月＝固定開銷＋機票 3000
#
# 先不要改這個檔：先在 checks_budget.py 寫一條 assert，證明它算錯了（跑起來會出現 AssertionError）。
# 證明完再回來修好它：nov、dec 都要從 fixed 複製一份（copy() 或 [:]），fixed 本身不能被改到。
fixed = [12000, 499]
nov = fixed
nov.append(120)
dec = fixed
dec.append(3000)
print("11 月合計", sum(nov), "元")
print("12 月合計", sum(dec), "元")
print("固定開銷", sum(fixed), "元")
