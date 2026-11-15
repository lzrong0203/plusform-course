# 1-11 第一圈：用 enumerate 替每一天編號（正確版）
week = [120, 85, 200, 95, 150, 60, 180]
for day, cost in enumerate(week, start=1):
    print("第", day, "天", cost, "元")
