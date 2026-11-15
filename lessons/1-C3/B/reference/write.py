# 檢核站 3 卷 B 第三部分的參考答案：從空的 dict 開始，一筆一筆加進那一種付款方式的合計（第一次遇到的，get 交回 0）；dict 記得放進去的順序，照第一次出現的順序印
pays = [("現金", 120), ("悠遊卡", 30), ("現金", 85), ("信用卡", 990), ("悠遊卡", 45)]
totals = {}
for way, amount in pays:
    totals[way] = totals.get(way, 0) + amount
for way, total in totals.items():
    print(way, total, "元")
