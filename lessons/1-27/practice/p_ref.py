# 矯正包練習：b = a 不是複製，兩個名字指著同一個 list（1-16）
# 先不要跑。在紙上畫一排格子，名字寫在左邊、畫箭頭指著它的格子；每跑一行就改一次。
# 寫下最後三行 print 各印出什麼，寫好再在帳本資料夾打 uv run lessons/1-27/practice/p_ref.py，對答案。
# 對不上的那一行，回 1-16 影片再看一次那一段（時間寫在矯正包.md）。
week = [100, 250]
same = week
same.append(80)
week.append(30)
other = [100, 250]
other.append(5)
print(week)
print(same)
print(other)
