# check 1-24 用的小程式（課程準備，學員不用改）：載入你的 ledger.py，另外做兩本帳本試試看
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):   # ledger.py 最下面自己印的不算
    from ledger import Entry, Ledger

a = Ledger()
b = Ledger()
print("新的帳本 total()：", a.total())
a.add(Entry("12/01", "書", 450))
a.add(Entry("12/02", "咖啡", 60))
print("a 有幾筆：", len(a.entries))
print("b 有幾筆：", len(b.entries))
print("a 最後一筆：", a.entries[-1].item)
print("a.total()：", a.total())
print("b.total()：", b.total())
