# 矯正包練習：dict 用鍵拿值、同一個鍵再放一次是換掉值、get 查不到交回預設值（1-15）
# 先不要跑。在紙上畫「鍵｜值」兩格一組的格子，每跑一行就改一次。
# 寫下最後兩行 print 各印出什麼，寫好再在帳本資料夾打 uv run lessons/1-C3/practice/p_dict.py，對答案。
budget = {"餐飲": 3000, "交通": 800}
budget["交通"] = 1000
budget["娛樂"] = budget.get("娛樂", 0) + 500
print(len(budget), budget["交通"], budget["娛樂"])
print(budget.get("醫療", 0), budget.get("餐飲", 0))
