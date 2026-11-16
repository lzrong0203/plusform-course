# 1-19 第①圈：熊的月報表（拆成函式之前的長版本）
# 同樣的步驟，為了兩種預算寫了兩次。這支不用改，split.py 要把它拆成五個小函式，跑出來要一模一樣。

nov = [("餐", 120), ("車", 30), ("餐", 85), ("書", 450), ("車", 60), ("餐", 300)]

# ===== 第一次：預算 1000 元 =====
print("== 11 月報表（預算 1000 元）==")

# 合計
s = 0
for kind, amount in nov:
    s = s + amount
print("合計", s, "元")

# 各分類的小計
cats = {}
for kind, amount in nov:
    cats[kind] = cats.get(kind, 0) + amount
for kind in cats:
    print(" ", kind, cats[kind], "元")

# 最大的一筆
big = nov[0]
for entry in nov:
    if entry[1] > big[1]:
        big = entry
print("最大的一筆", big[0], big[1], "元")

# 預算燈號（1-9）
ratio = s / 1000
if ratio < 0.8:
    print("綠燈")
elif ratio <= 1:
    print("黃燈")
else:
    print("紅燈")

# ===== 第二次：預算 1200 元（同樣的步驟再寫一次）=====
print("== 11 月報表（預算 1200 元）==")

s = 0
for kind, amount in nov:
    s = s + amount
print("合計", s, "元")

cats = {}
for kind, amount in nov:
    cats[kind] = cats.get(kind, 0) + amount
for kind in cats:
    print(" ", kind, cats[kind], "元")

big = nov[0]
for entry in nov:
    if entry[1] > big[1]:
        big = entry
print("最大的一筆", big[0], big[1], "元")

ratio = s / 1200
if ratio < 0.8:
    print("綠燈")
elif ratio <= 1:
    print("黃燈")
else:
    print("紅燈")
