# 1-17 第①圈：三段迴圈改成推導式，一段推導式改回迴圈（正確版）
amounts = [120, 85, 300, 45]

# 第一段：每一筆都用一張 20 元的折價券
cut = []
for a in amounts:
    cut.append(a - 20)
cut2 = [a - 20 for a in amounts]
assert cut2 == cut

# 第二段：只留 100 元以上的
big = []
for a in amounts:
    if a >= 100:
        big.append(a)
big2 = [a for a in amounts if a >= 100]
assert big2 == big

# 第三段：100 元以上的，才能用 20 元的折價券
use = []
for a in amounts:
    if a >= 100:
        use.append(a - 20)
use2 = [a - 20 for a in amounts if a >= 100]
assert use2 == use

# 改回來：for 和 if 的順序照抄，最前面的 a 變成 append 的括號裡
small = [a for a in amounts if a < 100]
small2 = []
for a in amounts:
    if a < 100:
        small2.append(a)
assert small2 == small

print(cut2)
print(big2)
print(use2)
print(small2)
