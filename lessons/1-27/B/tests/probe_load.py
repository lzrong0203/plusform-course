# 1-27 卷 B check 用的小程式（課程準備，學員不用改）：在暫存資料夾擺一個兩筆的帳本檔，用學員的 load 讀回來；再讀一個不存在的檔
import contextlib
import io
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()):
    import ledger_v1

p = Path("probe_ledger.txt")
p.write_bytes("12/01,早餐,65,熊\n12/02,書,380,兔\n".encode("utf-8"))
got = ledger_v1.load(p)
print(f"讀回 {len(got)} 筆")
for e in got:
    print(e.date, e.item, repr(e.amount), type(e.amount).__name__, e.payer)
print("不存在的檔：", ledger_v1.load(Path("沒有這個檔.txt")))
