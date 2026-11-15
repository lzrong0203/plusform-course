# 壞版本 1（課程準備，範例示意）：range(1, 7) 只到第 6 天
total = 0
for day in range(1, 7):
    print("第", day, "天：", end="")
    for cost in [60, 120, 150]:
        total = total + cost
        print(total, end=" ")
    print()
