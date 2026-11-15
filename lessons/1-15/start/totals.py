# 1-15 第①圈：各分類的小計和筆數（dict）
# entries 是這個月的每一筆帳：(分類, 金額)。照下面三步寫，印出三行（照 README「成品示範」）：
#   1. totals 放各分類的小計：先寫 totals = {}（空的 dict）；for kind, amount in entries: 拆包，
#      再寫 totals[kind] = totals.get(kind, 0) + amount（第一次遇到的分類，get 交回 0）
#   2. counts 放各分類記了幾筆：一樣從 {} 開始，用 counts.get(kind, 0) + 1
#   3. 用 for kind, amount in totals.items(): 一類印一行，例如「餐飲 205 元，2 筆」（筆數用 counts[kind] 拿）
# check 會把 entries 換成別的幾筆再跑一次，所以要用算的，不要把答案直接寫進 print。
entries = [("餐飲", 120), ("交通", 30), ("餐飲", 85), ("交通", 45), ("娛樂", 200)]

