# 1-17 第③圈：課程準備的報表程式（範例示意）。先讀懂它，再在 describe.md 用白話描述它在做什麼。
dates = ["11/01", "11/02", "11/03", "11/04"]
amounts = [120, 85, 300, 45]
for d, a in zip(dates, amounts):
    if a >= 100:
        print(d, a, "元")
big = [a for a in amounts if a >= 100]
print("100 元以上的有", len(big), "筆，合計", sum(big), "元")
