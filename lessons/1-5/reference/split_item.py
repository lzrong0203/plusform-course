# 1-5 第③圈：課程的正確版拆帳機（AI 照需求卡寫的，課程凍結的版本）
# 一行「品項 金額」，拆出品項（文字）和金額（整數）。你不用看懂這裡的寫法（def、return 之後的課會教），用 cases.txt 驗收它就好。
def split_item(text):
    parts = text.split()                         # 不帶參數：半形、全形的空白都算，連在一起的只算一個，前後的空白也不會拆出空的一段
    item = parts[0]                              # 第一段是品項
    amount = int(parts[-1].replace("元", ""))    # 最後一段是金額：先拿掉「元」，再變成整數
    return item, amount
