# 1-10 第②圈的參考寫法（影片裡熊用帶我寫跟家教一步一步組出來的那一支）：最多記 10 筆，打 q 也可以提早結束；空白的一行跳過、不算一筆
# 另一種寫法：while 的條件寫 count < 10（不用最後那個 if），check 一樣收
total = 0
count = 0
while True:
    text = input("金額，打 q 結束：")
    if text == "q":
        break
    if text == "":
        continue
    total = total + int(text)
    count = count + 1
    if count == 10:
        break
print("一共", count, "筆，合計", total, "元")
