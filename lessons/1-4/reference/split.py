# 1-4 第①圈的參考答案：果凍兔四個人去唱歌，一共 1450 元
# 第一步：總金額和人數
total = 1450
people = 4
# 第二步：每人先付多少、零頭幾元
each = total // people
left = total % people
# 第三步：印出來，最後一行驗算
print("每人", each, "元")
print("零頭", left, "元")
print("驗算", each * people + left)
