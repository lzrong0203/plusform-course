# 壞版本 2（課程準備，範例示意）：total = 0 放進外層迴圈裡，每天都從 0 重新算
for day in range(1, 8):
    total = 0
    print("第", day, "天：", end="")
    for cost in [60, 120, 150]:
        total = total + cost
        print(total, end=" ")
    print()
