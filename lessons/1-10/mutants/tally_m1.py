# 1-10 第③圈 壞版本 1（範例示意）：一問到就先算一筆，打 q 結束的時候，q 也被算成一筆
total = 0
count = 0
while True:
    text = input("金額，打 q 結束：")
    count = count + 1
    if text == "q":
        break
    if text == "":
        continue
    total = total + int(text)
print(f"一共 {count} 筆，合計 {total} 元")
