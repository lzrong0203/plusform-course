# 1-11 第一圈：7 天 × 3 餐的預算表（正確版）
for day in range(1, 8):
    print("第", day, "天：", end="")
    for cost in [60, 120, 150]:
        print(cost, end=" ")
    print()
