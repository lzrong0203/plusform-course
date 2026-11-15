# 矯正包練習：for 後面拆包、set 去掉重複（1-14）
# 先不要跑。每一圈寫下 place、cost 是什麼，names 和 costs 變成什麼；最後 places 把重複的拿掉，剩幾個？
# 寫下最後兩行 print 各印出什麼，寫好再在帳本資料夾打 uv run lessons/1-C3/practice/p_set.py，對答案。
# 提示：set 沒有保證順序，所以這裡只印有幾個（len），不印 set 本身。
visits = [("超商", 45), ("早餐店", 60), ("超商", 30), ("超商", 25)]
names = []
costs = []
for place, cost in visits:
    names.append(place)
    costs.append(cost)
places = set(names)
print(len(names), len(places), len(costs))
print(sum(costs))
