# 1-27 check 用的小程式（課程準備，學員不用改）：載入學員的 ledger_v1.py，試幾種寫得對的金額
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):   # 學員檔案最下面自己印的不算
    import ledger_v1

for t in ["120", "120元", "1,200", "2,050元"]:
    try:
        v = ledger_v1.to_yuan(t)
        print(f"to_yuan({t!r}) → {v!r}（{type(v).__name__}）")
    except Exception as e:
        print(f"to_yuan({t!r}) → 丟出 {type(e).__name__}：{e}")
