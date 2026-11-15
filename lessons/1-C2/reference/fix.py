# 檢核站 2　第二部分的正確版（老師用）：三個地方要修——
#   1. input 交回來的一定是字串：budget - price 跳出 TypeError（錯誤出現在減法那一行，要改的是上面拿價錢的那一行，1-6、1-7）
#   2. 加上 int() 以後，打 65元 跳出 ValueError：int() 看不懂「元」，先用 replace 拿掉（1-5、1-6）
#   3. 剛好花完也算在預算內：left > 0 要改成 left >= 0（1-8、1-9）
budget = 300
item = input("品項：")
price = int(input("價錢：").replace("元", ""))
left = budget - price
print(f"{item} {price} 元")
print(f"還剩 {left} 元")
if left >= 0:
    print("還在預算內")
else:
    print("超過預算了")
