# Lv1 上關卡（卷 B）　第一部分：fix.py 修好的樣子（參考答案）
count = 0
money = 0
while True:
    text = input("一杯多少錢，打 q 結束：")
    if text == "q":
        break
    if text == "":
        continue
    count = count + 1
    money = money + int(text)
print("一共", count, "杯")
print("合計", money, "元")
