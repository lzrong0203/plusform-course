# 1-10 第③圈 壞版本 2（範例示意）：先問一次、迴圈最後再問一次的寫法；空白的那一行 continue 跳回 while，
# 下面「再問一次」那一行被跳過，text 一直是空的 → 無窮迴圈（check 跑到逾時把它停下來）
total = 0
count = 0
text = input("金額，打 q 結束：")
while text != "q":
    if text == "":
        continue
    total = total + int(text)
    count = count + 1
    text = input("金額，打 q 結束：")
print(f"一共 {count} 筆，合計 {total} 元")
