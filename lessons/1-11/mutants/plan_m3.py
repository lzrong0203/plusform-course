# 壞版本 3（課程準備，範例示意）：換行的 print() 縮進了內層迴圈，每一格自己一列
total = 0
for day in range(1, 8):
    print("第", day, "天：", end="")
    for cost in [60, 120, 150]:
        total = total + cost
        print(total, end=" ")
        print()
