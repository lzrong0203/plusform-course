# 果凍兔今天的收據（課程版本：AI 照需求卡寫的）
money = 300
juice = 50
dinner = 130
mrt = 25
print("果汁", juice, "元")
print("晚餐", dinner, "元")
print("捷運", mrt, "元")
total = sum([juice, dinner, mrt])
print("合計", total, "元")
food = sum([juice, dinner])
print("飲食", food, "元")
money = money - total
print("錢包剩下", money, "元")
