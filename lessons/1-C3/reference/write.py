# 檢核站 3 第三部分的參考答案：從空的 dict 開始，一筆一筆加進那一類的合計（第一次遇到的分類，get 交回 0）；dict 記得放進去的順序，照第一次出現的順序印
records = [("早餐", 60), ("午餐", 120), ("早餐", 45), ("飲料", 65), ("午餐", 90)]
totals = {}
for kind, amount in records:
    totals[kind] = totals.get(kind, 0) + amount
for kind, total in totals.items():
    print(kind, total, "元")
