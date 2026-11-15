# 1-11 第三圈：AI 交回的伙食預算表 plan.py（課程準備的正確版，範例示意）
# 每天一列，三格依序是早餐、午餐、晚餐；每一格是「到這一餐為止，這週一共要準備多少錢」
total = 0
for day in range(1, 8):
    print("第", day, "天：", end="")
    for cost in [60, 120, 150]:
        total = total + cost
        print(total, end=" ")
    print()
