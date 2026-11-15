# 1-16 第①圈：果凍兔的兩本帳本（正確版：各自複製一份）
start = []
bear = start.copy()
rabbit = start.copy()
bear.append(120)
rabbit.append(300)
print("熊的帳", bear)
print("兔的帳", rabbit)
print("是同一本嗎", bear is rabbit)
