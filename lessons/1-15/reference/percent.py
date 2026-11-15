# 1-15 第②圈：各分類占了幾 % 的參考答案
totals = {"餐飲": 205, "交通": 75, "娛樂": 200}

whole = sum(totals.values())
for kind, amount in totals.items():
    print(kind, round(amount / whole * 100, 1), "%")
