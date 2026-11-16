# 1-20 第①圈：依金額由小到大排；金額一樣的，再依日期由早到晚。
# entries 那一行不要改（check 會換成別的資料，再跑一次）。最下面兩行也不要改。
# 提示：sorted 是穩定排序（key 一樣大的，照原本的順序）。先照日期排一次，再照金額排一次。
#       key 可以用 lambda，也可以用 def 寫的函式。
# 寫完在帳本資料夾跑：uv run lessons/1-20/sort2.py

entries = [("11/03", "餐", 120), ("11/01", "車", 85), ("11/02", "書", 120), ("11/04", "餐", 85)]

result = entries   # 改這一行（可以寫成好幾行）

for date, cat, amount in result:
    print(date, cat, amount)
