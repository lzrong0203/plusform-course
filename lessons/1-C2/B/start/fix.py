# 檢核站 2　卷 B　第二部分：修好這支程式（關掉 AI）
# 熊要記一份早餐：程式問品項和價錢，印出這一筆，再算這週一共花了多少。這週的預算 300 元，剛好花到 300，也算在預算內。
# 在帳本資料夾打 uv run lessons/1-C2B/fix.py，品項打 蛋餅、價錢打 45元（照打，「元」也打），修好以後要印出這三行：
#   蛋餅 45 元
#   這週花了 165 元
#   還在預算內
# 跑起來跳出錯誤訊息，就從最下面一行看起；修好一個，存檔，再跑一次。
spent = 120
budget = 300
item = input("品項：")
price = input("價錢：")
spent = spent + price
print(f"{item} {price} 元")
print(f"這週花了 {spent} 元")
if spent < budget:
    print("還在預算內")
else:
    print("超過預算了")
