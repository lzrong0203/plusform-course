# 1-6 第③圈：壞版本 3（課程準備的）
budget = 3000
print(f"這週的餐費預算 {budget} 元")

item = input("品項：").strip()
amount = input("金額：").replace(",", "")

print(f"記下來了：{item} {amount}元")
print(f"這週還剩 {budget - amount} 元")
