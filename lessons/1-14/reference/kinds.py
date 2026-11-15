# 1-14 第①圈：兩個月的分類的參考答案
nov = ["餐飲", "交通", "餐飲", "娛樂", "交通", "餐飲"]
dec = ["交通", "醫療", "交通", "餐飲"]

nov_kinds = set(nov)
dec_kinds = set(dec)
print("11 月一共", len(nov), "筆，花在", len(nov_kinds), "種分類")
print("兩個月都有", sorted(nov_kinds & dec_kinds))
print("只有 11 月有", sorted(nov_kinds - dec_kinds))
