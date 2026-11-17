# 1-24 第③圈：biggest 的需求寫在 docstring，交給 AI 寫；你用 assert 驗收
# ledger_ai.py 是 AI 交回來的版本（課程準備的固定版本，範例示意，不要改它）。
from ledger_ai import Entry, Ledger

# Ledger.biggest() 的需求（docstring）：交回金額最大的那一筆 Entry；帳本是空的，交回 None。
# 每一條檢查都長這樣：先把帳加進一本 Ledger，再 assert book.biggest() == 你算好的那一筆

book = Ledger()
book.add(Entry("11/03", "午餐", 120))
assert book.biggest() == Entry("11/03", "午餐", 120)

# 換你寫：至少再兩條。想想 AI 最容易寫錯哪裡：空的帳本？最大的那一筆不在最前面、也不在最後面？
