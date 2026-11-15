# Lv1 上關卡　第一部分：fix.py 修好的樣子（參考答案）
count = 0
total = 0
while True:
    text = input("金額，打 q 結束：")
    if text == "q":
        break
    if text == "":
        continue
    count = count + 1
    total = total + int(text)
print("一共", count, "筆")
print("合計", total, "元")
