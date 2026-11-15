# 1-10 第②圈的參考寫法：最多記 10 筆，打 q 也可以提早結束；空白的一行跳過、不算一筆
total = 0
count = 0
while count < 10:
    text = input("金額，打 q 結束：")
    if text == "q":
        break
    if text == "":
        continue
    total = total + int(text)
    count = count + 1
print(f"一共 {count} 筆，合計 {total} 元")
