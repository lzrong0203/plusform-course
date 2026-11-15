# 1-15 第②圈：各分類占了幾 %（影片裡熊跟家教一步一步寫出來的那一支）
# totals 是各分類的小計。照影片裡的步驟寫：
#   1. 先算全部加起來是多少：sum 裡放 totals.values()（只寫 sum(totals)，加的是鍵，會出現 TypeError）
#   2. for kind, amount in totals.items(): 一類一類拿出來
#   3. 小計 ÷ 全部 × 100，用 round 留到小數一位，一類印一行，例如「餐飲 42.7 %」
# check 會把 totals 換成別的再跑一次，所以要用算的，不要把答案直接寫進 print。
totals = {"餐飲": 205, "交通": 75, "娛樂": 200}

