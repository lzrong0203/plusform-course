# 1-6 第③圈：壞版本 2（課程準備的）
budget = 3000
print(f"這週的餐費預算 {budget} 元")

item = input("品項：").strip()
amount = int(input("金額："))

print(f"記下來了：{item} {amount}元")
print(f"這週還剩 {budget - amount} 元")
