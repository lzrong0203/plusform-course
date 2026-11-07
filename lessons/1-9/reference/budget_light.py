# 1-9 正確版：預算燈號
spent = int(input("這個月花了多少？"))
budget = int(input("預算是多少？"))
ratio = spent / budget

if ratio < 0.8:
    print("綠燈")
elif ratio <= 1:
    print("黃燈")
else:
    print("紅燈")
