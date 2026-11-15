# 1-18 第①圈：把加總包成函式（正確版）


def total(amounts):
    s = 0
    for a in amounts:
        s = s + a
    return s


nov = [120, 85, 300]
dec = [65, 200]

print("11 月合計", total(nov), "元")
print("12 月合計", total(dec), "元")
