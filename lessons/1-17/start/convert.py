# 1-17 第①圈：三段迴圈改成推導式，一段推導式改回迴圈
# 先讀懂每一段，照提示改寫，再用 assert 確認兩種寫法的結果一樣。
# amounts 那一行不要改（check 會換成別的金額再跑一次）；最後四行 print 也不要改。
amounts = [120, 85, 300, 45]

# 第一段：每一筆都用一張 20 元的折價券
cut = []
for a in amounts:
    cut.append(a - 20)
cut2 = []   # ← 改成一行推導式：cut2 = [… for a in amounts]
assert cut2 == cut

# 第二段：只留 100 元以上的
big = []
for a in amounts:
    if a >= 100:
        big.append(a)
big2 = []   # ← 改成一行推導式
assert big2 == big

# 第三段：100 元以上的，才能用 20 元的折價券
use = []
for a in amounts:
    if a >= 100:
        use.append(a - 20)
use2 = []   # ← 改成一行推導式
assert use2 == use

# 改回來：把下面這一行推導式改回迴圈（small2 = [] 留著，在它下面寫 for、if、append）
small = [a for a in amounts if a < 100]
small2 = []
assert small2 == small

print(cut2)
print(big2)
print(use2)
print(small2)
