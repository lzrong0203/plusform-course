# 1-27 卷 B check 用的小程式（課程準備，學員不用改）：用學員的 save 存兩筆、再存一筆（整個檔案重寫），印出檔案裡真的寫了什麼
import contextlib
import io
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()):
    import ledger_v1

E = ledger_v1.Entry
p = Path("probe_out.txt")
ledger_v1.save(p, [E("12/01", "早餐", 65, "熊"), E("12/02", "書", 380, "兔")])
print("存兩筆：", repr(p.read_bytes().decode("utf-8")))
ledger_v1.save(p, [E("12/05", "飲料", 50, "熊")])
print("再存一筆：", repr(p.read_bytes().decode("utf-8")))
