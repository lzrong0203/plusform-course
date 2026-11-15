# 矯正包練習：strip、split、replace、f-string 的千分位（1-5）
# 先不要跑。在紙上寫下每一行 print 會印出什麼（前後有沒有空白也想一想）。
# 寫好再在帳本資料夾打 uv run lessons/1-C2/practice/p_str.py 對答案。
# 對不上的那一行，回 1-5 影片再看一次那一段（時間寫在矯正包.md）。
line = "  咖啡 1500元  "
print("[" + line.strip() + "]")
parts = line.split()
print(parts[0])
print(parts[-1].replace("元", ""))
amount = int(parts[-1].replace("元", ""))
print(f"{parts[0]} {amount:,} 元")
print(f"三杯 {amount * 3:,} 元")
