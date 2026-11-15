# 1-17 第①圈：用 zip 把日期和金額配成一對對（正確版）
dates = ["11/01", "11/02", "11/03", "11/04"]
amounts = [120, 85, 300, 45]

assert len(dates) == len(amounts)
for d, a in zip(dates, amounts):
    print(d, a, "元")
