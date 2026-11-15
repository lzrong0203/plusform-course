# 1-15 第①圈：各分類的小計和筆數的參考答案
entries = [("餐飲", 120), ("交通", 30), ("餐飲", 85), ("交通", 45), ("娛樂", 200)]

totals = {}
counts = {}
for kind, amount in entries:
    totals[kind] = totals.get(kind, 0) + amount
    counts[kind] = counts.get(kind, 0) + 1
for kind, amount in totals.items():
    print(f"{kind} {amount} 元，{counts[kind]} 筆")
