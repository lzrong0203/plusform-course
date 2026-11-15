# 檢核站 3 拼圖的排法（正確版）：amounts 和 over = [] 只做一次，放在最上面；for 一天一天看，超過 100 的才印、才放進 over（兩行都縮在 if 底下，誰先誰後都可以）；一共幾天只印一次，放最後、不縮排
amounts = [80, 120, 95, 300]
over = []
for i, a in enumerate(amounts, start=1):
    if a > 100:
        print("第", i, "天", a, "元")
        over.append(a)
print("一共", len(over), "天超過 100 元")
