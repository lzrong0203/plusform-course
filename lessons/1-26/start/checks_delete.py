# 1-26 第③圈：「刪除前要先確認」寫在 docstring，交給 AI 寫；你用 assert 驗收
# delete_ai.py 是 AI 交回來的版本（課程準備的固定版本，範例示意，不要改它）。
from delete_ai import Entry, delete_entry

# delete_entry(entries, no, confirm=False) 的需求（docstring）：
#   刪掉第 no 筆（no 跟 show 印的編號一樣，從 1 開始），刪除前要先確認：
#   confirm 是 False（沒寫就是 False）只交回要刪的那一筆、不刪；是 True 才從 entries 拿掉，也交回那一筆
#   編號不在 1 到筆數之間：丟 ValueError，什麼都不刪

lunch = Entry("11/03", "午餐", 120)
bus = Entry("11/04", "公車", 15)
dinner = Entry("11/05", "晚餐", 180)

book = [lunch, bus, dinner]
delete_entry(book, 2, confirm=True)
assert len(book) == 2          # 範例：確認以後少了一筆

# 換你寫：至少再三條（用 book = [lunch, bus, dinner] 重新擺一次三筆）。
# 想想 AI 最容易寫錯哪裡：刪掉的是不是那一筆？沒確認的時候真的沒刪嗎？編號 0 呢？
