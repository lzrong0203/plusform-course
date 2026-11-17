# 1-27 卷 B check 用的小程式（課程準備，學員不用改）：用學員的 by_payer 加總四筆，再試沒有帳
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    import ledger_v1

E = ledger_v1.Entry
book = [E("12/01", "早餐", 65, "熊"), E("12/02", "書", 380, "兔"), E("12/03", "晚餐", 200, "熊"), E("12/05", "飲料", 50, "海豹")]
print("四筆：", ledger_v1.by_payer(book))
print("沒有帳：", ledger_v1.by_payer([]))
