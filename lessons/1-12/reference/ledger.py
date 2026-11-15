# Lv1 上關卡　第一部分：帳本 v0.1 的參考寫法（寫法不只一種，check 照印出來的結果判）
budget = int(input("預算："))
food = 0
traffic = 0
other = 0
while True:
    kind = input("分類，打 q 結束：")
    if kind == "q":
        break
    amount = int(input("金額："))
    if kind == "餐飲":
        food = food + amount
    elif kind == "交通":
        traffic = traffic + amount
    else:
        other = other + amount
total = food + traffic + other
print("餐飲", food, "元")
print("交通", traffic, "元")
print("其他", other, "元")
print("合計", total, "元")
ratio = total / budget
if ratio < 0.8:
    print("綠燈")
elif ratio <= 1:
    print("黃燈")
else:
    print("紅燈")
people = int(input("幾個人分："))
print("每人", total // people, "元，零頭", total % people, "元")
