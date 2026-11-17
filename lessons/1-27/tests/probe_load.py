# 1-27 check 用的小程式（課程準備，學員不用改）：在暫存資料夾擺一個兩筆的帳本檔，用學員的 load 讀回來；再讀一個不存在的檔
import contextlib
import io
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()):
    import ledger_v1

p = Path("probe_ledger.txt")
p.write_bytes("11/03,午餐,餐飲,120\n11/04,公車,交通,15\n".encode("utf-8"))
got = ledger_v1.load(p)
print(f"讀回 {len(got)} 筆")
for e in got:
    print(e.date, e.item, e.category, repr(e.amount), type(e.amount).__name__)
print("不存在的檔：", ledger_v1.load(Path("沒有這個檔.txt")))
