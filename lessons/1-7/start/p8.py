# 從一筆帳拿出金額，算這週還剩多少
line = "2026-11-07 午餐 120"
parts = line.split()
amount = parts[1]
left = 3000 - int(amount)
print("這週還剩", left, "元")
