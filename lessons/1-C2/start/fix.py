# 檢核站 2　第二部分：修好這支程式（關掉 AI）
# 果凍兔要記一杯飲料：程式問品項和價錢，印出這一筆，再算這週的零用錢還剩多少。剛好花完，也算在預算內。
# 在帳本資料夾打 uv run lessons/1-C2/fix.py，品項打 珍奶、價錢打 65元（照打，「元」也打），修好以後要印出這三行：
#   珍奶 65 元
#   還剩 235 元
#   還在預算內
# 跑起來跳出錯誤訊息，就從最下面一行看起；修好一個，存檔，再跑一次。
budget = 300
item = input("品項：")
price = input("價錢：")
left = budget - price
print(f"{item} {price} 元")
print(f"還剩 {left} 元")
if left > 0:
    print("還在預算內")
else:
    print("超過預算了")
