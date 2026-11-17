# 1-27 check 用的小程式（課程準備，學員不用改）：用學員的 totals 加總三筆，再試沒有帳
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    import ledger_v1

E = ledger_v1.Entry
book = [E("11/03", "午餐", "餐飲", 120), E("11/04", "公車", "交通", 15), E("11/05", "晚餐", "餐飲", 180), E("11/06", "電影", "娛樂", 280)]
print("四筆：", ledger_v1.totals(book))
print("沒有帳：", ledger_v1.totals([]))
