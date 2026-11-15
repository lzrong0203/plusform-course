# 1-17 第③圈：正確版（照 describe.md 的描述寫得出來的一種；學員貼進來的是 AI 寫的，寫法不一定一樣，check 只跑測試）
dates = ["11/01", "11/02", "11/03", "11/04"]
amounts = [120, 85, 300, 45]

days = [(d, a) for d, a in zip(dates, amounts) if a >= 100]
for d, a in days:
    print(d, a, "元")
print("100 元以上的有", len(days), "筆，合計", sum([a for d, a in days]), "元")
