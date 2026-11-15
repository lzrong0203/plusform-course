# 1-10 第③圈：課程準備的正確版（範例示意，事先準備、固定不再改）
# 需求：一直記到打 q 為止；q 不算一筆；空白的一行（不小心多按一下 Enter）跳過、也不算一筆；最後印出一共幾筆、合計多少
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
print(f"一共 {count} 筆，合計 {total} 元")
