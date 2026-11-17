# 1-27 第一部分（卷 A）　拼圖（2 題）
# 熊把一串打進來的金額加起來，看不懂的（例如 abc）不算進去、另外數有幾筆。
# 下面十一行的順序被打亂了，也沒有縮排。把它們排回正確的順序、自己加縮排（每一層四個空格）。
# 規定：只能搬動和縮排，不能改字、不能多寫、不能少寫（這幾行 # 開頭的說明可以留着）。
# 排好跑起來，要印出這一行：
#   合計 200 元，看不懂 1 筆
# 排好存檔，在帳本資料夾打 uv run lessons/1-27/parsons.py 跑跑看。
bad = bad + 1
s, n = add_up(["120", "abc", "80"])
for t in texts:
except ValueError:
return total, bad
total = 0
try:
print(f"合計 {s} 元，看不懂 {n} 筆")
def add_up(texts):
total = total + int(t)
bad = 0
