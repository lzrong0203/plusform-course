# 1-11 拼圖（Parsons）的排法（正確版）：n = 0 只做一次，放在最外面；外層 3 天裡面跑內層 3 餐，n 加 1 和 print 都在內層裡
n = 0
for day in range(1, 4):
    for cost in [60, 120, 150]:
        n = n + 1
        print("第", n, "餐：第", day, "天，預算", cost, "元")
