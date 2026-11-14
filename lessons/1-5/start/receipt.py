# 1-5 第①圈：把帳本的一行，排成收據的一行
# 把三個 ？ 換掉，存檔，再在帳本資料夾裡跑：uv run lessons/1-5/receipt.py
# 跑出來要是這一行：12月25日 聖誕大餐 1,280元
line = " 2026-12-25 聖誕大餐 1280 "

# 第一步：拿掉前後的空白，再用空白拆成三段
parts = line.strip().split()
date = parts[0]
item = parts[1]
amount = int(parts[2])

# 第二步：從日期切出月和日（月是索引 5、6 那兩個字，日是最後兩個字）
month = ？
day = ？

# 第三步：用 f-string 排成一行，金額要有千分位的逗號
print(？)
