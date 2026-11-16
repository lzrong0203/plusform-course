# 1-19 第①圈：修好「預設值用 []」的陷阱
# 下面的 add_entry：沒給帳本時，應該開一本新的。可是現在兩次呼叫共用同一個 list
# （預設值只在 Python 讀到 def 那一行的時候做一次）。先跑一次看看印出什麼。
# 照官方教學的寫法改：預設值改成 None，函式裡 book 是 None 的時候，才做一個新的空 list。
# 最下面三行不要改。改好以後要印出：[120] [65]
# check 會跑這支程式，也會直接呼叫 add_entry 好幾次（沒給帳本、給了帳本都會試）。


def add_entry(amount, book=[]):
    book.append(amount)
    return book


nov = add_entry(120)
dec = add_entry(65)
print(nov, dec)
