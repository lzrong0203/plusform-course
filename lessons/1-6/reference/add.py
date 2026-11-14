# 1-6 第③圈：課程的正確版記帳程式（AI 照需求卡寫的，課程凍結的版本）
# 先印這週的餐費預算，再問品項和金額，印出記下來的和還剩多少。你不用看懂這裡的寫法，用 inputs.txt 和 expected.txt 驗收它就好。
budget = 3000
print(f"這週的餐費預算 {budget} 元")

item = input("品項：").strip()                    # 品項前後多打的空白不算
amount = int(input("金額：").replace(",", ""))    # 有人會打千分位逗號：先拿掉逗號，再變成整數

print(f"記下來了：{item} {amount}元")
print(f"這週還剩 {budget - amount} 元")
