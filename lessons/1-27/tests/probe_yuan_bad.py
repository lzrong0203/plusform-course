# 1-27 check 用的小程式（課程準備，學員不用改）：載入學員的 ledger_v1.py，試幾種不合法的金額
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    import ledger_v1

for t in ["八十", "0", "-35元"]:
    try:
        v = ledger_v1.to_yuan(t)
        print(f"to_yuan({t!r}) → 沒有丟出錯誤，交回 {v!r}")
    except ValueError as e:
        print(f"to_yuan({t!r}) → ValueError，訊息裡{'有' if t.replace('元', '') in str(e) else '沒有'} {t.replace('元', '')}")
    except Exception as e:
        print(f"to_yuan({t!r}) → 丟出 {type(e).__name__}（應該是 ValueError）")
