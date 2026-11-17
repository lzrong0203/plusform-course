# 1-27 第一部分（卷 B）　拼圖（2 題）
# 熊在一串打進來的金額裡找最大的，看不懂的（例如 ?、八十）不算進去、另外數有幾筆。
# 下面十一行的順序被打亂了，也沒有縮排。把它們排回正確的順序、自己加縮排（每一層四個空格）。
# 規定：只能搬動和縮排，不能改字、不能多寫、不能少寫（這幾行 # 開頭的說明可以留着）。
# 排好跑起來，要印出這一行：
#   最大 300 元，看不懂 2 筆
# 排好存檔，在帳本資料夾打 uv run lessons/1-27B/parsons.py 跑跑看。
except ValueError:
best = 0
print(f"最大 {m} 元，看不懂 {n} 筆")
for t in texts:
return best, bad
def biggest_ok(texts):
bad = bad + 1
m, n = biggest_ok(["45", "?", "300", "八十"])
best = max(best, int(t))
try:
bad = 0
