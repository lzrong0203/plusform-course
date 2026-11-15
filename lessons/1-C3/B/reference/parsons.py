# 檢核站 3 卷 B 拼圖的排法（正確版）：fares 和 taxi = [] 只做一次，放在最上面；for 一趟一趟看，100 元以上的才印、才放進 taxi（兩行都縮在 if 底下，誰先誰後都可以）；一共幾趟只印一次，放最後、不縮排
fares = [15, 180, 25, 220]
taxi = []
for i, f in enumerate(fares, start=1):
    if f >= 100:
        print("第", i, "趟", f, "元")
        taxi.append(f)
print("一共", len(taxi), "趟 100 元以上")
