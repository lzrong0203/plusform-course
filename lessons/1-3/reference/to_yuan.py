# 1-3 第③圈：課程的正確版轉換機（AI 照需求卡寫的，課程凍結的版本）
# 把金額文字變成整數元。你不用看懂這裡的寫法（def、replace、int() 之後的課會教），用 cases.txt 驗收它就好。
def to_yuan(text):
    text = text.replace(",", "")   # 拿掉千分位的逗號：1,200 → 1200
    text = text.replace("元", "")  # 拿掉「元」：85元 → 85
    return int(text)               # 變成整數（前後的空白，int() 會自己忽略）
