# 1-16 第③圈：兩個月的預算（壞版本 2：只有 nov 複製了一份，dec 還是直接等於 fixed：12 月的機票加進了固定開銷）
# 每個月都有的固定開銷 fixed：房租 12000、手機 499
# nov：11 月＝固定開銷＋午餐 120；dec：12 月＝固定開銷＋機票 3000
fixed = [12000, 499]
nov = fixed.copy()
nov.append(120)
dec = fixed
dec.append(3000)
print("11 月合計", sum(nov), "元")
print("12 月合計", sum(dec), "元")
print("固定開銷", sum(fixed), "元")
