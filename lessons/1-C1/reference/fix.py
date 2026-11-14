# 檢核站 1　第二部分的正確版（老師用）：三個地方要修——少一個引號（SyntaxError，1-1）、"60" 是文字不能跟整數相加（TypeError，1-3）、平均只留整數元要用 //（1-4）
day1 = 45
day2 = 60
day3 = 55
total = day1 + day2 + day3
print("一共", total, "元")
print("平均", total // 3, "元")
