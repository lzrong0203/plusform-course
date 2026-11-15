# 矯正包練習：切片拿到的是字串、int() 變成整數、// 除完只留整數（1-5、1-4）
# 先不要跑。在紙上寫下三行各印出什麼（索引從 0 開始；切到結束那一格之前）。
# 再用 uv run lessons/1-12/practice/p_slice.py 跑，對答案。
line = "2026-07-04 早餐 95"
print(line[5:7], line[8:10])
price = int(line[-2:])
print(price // 2, price % 2)
print(f"{line[5:7]} 月 {price // 4} 元")
