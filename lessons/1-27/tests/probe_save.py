# 1-27 check 用的小程式（課程準備，學員不用改）：用學員的 save 存兩筆、再存一筆（整個檔案重寫），印出檔案裡真的寫了什麼
import contextlib
import io
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()):
    import ledger_v1

E = ledger_v1.Entry
p = Path("probe_out.txt")
ledger_v1.save(p, [E("11/03", "午餐", "餐飲", 120), E("11/04", "公車", "交通", 15)])
print("存兩筆：", repr(p.read_bytes().decode("utf-8")))
ledger_v1.save(p, [E("11/05", "晚餐", "餐飲", 180)])
print("再存一筆：", repr(p.read_bytes().decode("utf-8")))
