# 1-15 第①圈：預算燈號 dict 對照表的參考答案
spent = int(input("這個月花了多少？"))
limits = {"綠燈": 799, "黃燈": 1000}

light = "紅燈"
for name, top in limits.items():
    if spent <= top:
        light = name
        break
print(light)
