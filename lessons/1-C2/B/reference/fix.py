# 檢核站 2　卷 B　第二部分的正確版（老師用）：三件事要修——
#   1. input 交回來的一定是字串：spent + price 跳出 TypeError（錯誤出現在加法那一行，要改的是上面拿價錢的那一行，1-6、1-7）
#   2. 加上 int() 以後，打 45元 跳出 ValueError：int() 看不懂「元」，先用 replace 拿掉（1-5、1-6）
#   3. 剛好花到預算也算在預算內：spent < budget 要改成 spent <= budget（1-8、1-9）
spent = 120
budget = 300
item = input("品項：")
price = int(input("價錢：").replace("元", ""))
spent = spent + price
print(f"{item} {price} 元")
print(f"這週花了 {spent} 元")
if spent <= budget:
    print("還在預算內")
else:
    print("超過預算了")
