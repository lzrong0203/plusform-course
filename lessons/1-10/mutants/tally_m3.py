# 1-10 第③圈 壞版本 3（範例示意）：合計沒有累加，每一筆都蓋掉前一筆，只記到最後一筆
total = 0
count = 0
while True:
    text = input("金額，打 q 結束：")
    if text == "q":
        break
    if text == "":
        continue
    total = int(text)
    count = count + 1
print(f"一共 {count} 筆，合計 {total} 元")
