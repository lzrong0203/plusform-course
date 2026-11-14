# 1-5 第①圈的參考答案：把帳本的一行，排成收據的一行
line = " 2026-12-25 聖誕大餐 1280 "

# 第一步：拿掉前後的空白，再用空白拆成三段
parts = line.strip().split()
date = parts[0]
item = parts[1]
amount = int(parts[2])

# 第二步：從日期切出月和日（月是索引 5、6 那兩個字，日是最後兩個字）
month = date[5:7]
day = date[-2:]

# 第三步：用 f-string 排成一行，金額要有千分位的逗號
print(f"{month}月{day}日 {item} {amount:,}元")
