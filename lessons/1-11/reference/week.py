# 1-11 第一圈：一週七天的花費（正確版）
week = [120, 85, 200, 95, 150, 60, 180]
total = 0
count = 0
biggest = 0
for cost in week:
    total = total + cost
    if cost > 150:
        count = count + 1
    if cost > biggest:
        biggest = cost
print("一週一共", total, "元")
print("超過預算", count, "天")
print("最多的一天", biggest, "元")
