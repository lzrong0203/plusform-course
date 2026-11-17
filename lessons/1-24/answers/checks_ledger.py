# 1-24 第③圈：老師的標準檢查（跟影片裡熊寫的一樣：空的帳本、一筆、三筆裡最大的在中間）
from ledger_ai import Entry, Ledger

book = Ledger()
assert book.biggest() is None
book.add(Entry("11/03", "午餐", 120))
assert book.biggest() == Entry("11/03", "午餐", 120)
book.add(Entry("11/05", "晚餐", 180))
book.add(Entry("11/04", "公車", 15))
assert book.biggest() == Entry("11/05", "晚餐", 180)
