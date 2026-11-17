# check 1-24 用的小程式（課程準備，學員不用改）：載入你的 entry.py，用 Entry 另外做幾筆帳試試看
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):   # entry.py 最下面自己印的不算
    from entry import Entry

book = Entry("12/01", "書", 450)
print("屬性：", book.date, book.item, book.amount)
print("印出來：", book)
print("一樣的兩筆用 == 比：", book == Entry("12/01", "書", 450))
print("金額不一樣用 == 比：", book == Entry("12/01", "書", 451))
try:
    Entry("12/01", "書")
    print("少給金額：沒有擋下來")
except TypeError:
    print("少給金額：TypeError")
