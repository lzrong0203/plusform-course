# 檢核站 1（卷 B）第二部分的正確版（老師用）：三個地方要修——少一個引號（SyntaxError，1-1）、"70" 是文字不能跟整數相加（TypeError，1-3）、平均只留整數元要用 //（1-4）
mon = 85
tue = 90
wed = 70
total = mon + tue + wed
print("一共", total, "元")
print("平均", total // 3, "元")
