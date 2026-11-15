# 1-10 第①圈的參考寫法：一直記到打 q 為止，空白的一行跳過，最後印出一共多少錢
total = 0
while True:
    text = input("金額，打 q 結束：")
    if text == "q":
        break
    if text == "":
        continue
    total = total + int(text)
    print("目前合計", total, "元")
print("一共", total, "元")
