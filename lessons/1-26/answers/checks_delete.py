# 1-26 第③圈：老師的標準檢查（跟影片裡熊寫的一樣：先確認交回公車、沒確認不刪、確認以後剩午餐和晚餐、編號 0 丟 ValueError）
from delete_ai import Entry, delete_entry

lunch = Entry("11/03", "午餐", 120)
bus = Entry("11/04", "公車", 15)
dinner = Entry("11/05", "晚餐", 180)

book = [lunch, bus, dinner]
assert delete_entry(book, 2) == bus
assert book == [lunch, bus, dinner]
assert delete_entry(book, 2, confirm=True) == bus
assert book == [lunch, dinner]
try:
    delete_entry(book, 0, confirm=True)
except ValueError:
    pass
else:
    assert False, "編號 0 應該丟 ValueError"
assert book == [lunch, dinner]
