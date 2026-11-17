# check 1-26 用的小程式（課程準備，學員不用改）：載入你的 old_ledger.py，在暫存資料夾另外擺三筆帳，呼叫 delete 指令試試看
import contextlib
import io
import tempfile
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()):   # 載入時印的不算
    import old_ledger as L

L.DATA = Path(tempfile.mkdtemp(prefix="plusform-probe-")) / "old_ledger.txt"   # 存檔寫到暫存資料夾，不碰你的 old_ledger.txt
print("有 delete 這個指令：", "delete" in L.COMMANDS)
entries = [L.Entry("11/03", "午餐", 120), L.Entry("11/04", "公車", 15), L.Entry("11/05", "晚餐", 180)]
with contextlib.redirect_stdout(io.StringIO()):
    L.COMMANDS["delete"](entries, "2")
print("刪掉第 2 筆以後：", [e.item for e in entries])
print("存進檔案的：", L.DATA.read_text(encoding="utf-8").splitlines())
with contextlib.redirect_stdout(io.StringIO()):
    L.COMMANDS["delete"](entries, "2")
print("再刪第 2 筆以後：", [e.item for e in entries])
