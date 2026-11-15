# 1-16 第①圈：用 is 檢查兩個名字是不是同一個 list（正確版）
a = [120, 85]
b = a
c = a.copy()
print(a is b)
print(a is c)
print(a == c)
