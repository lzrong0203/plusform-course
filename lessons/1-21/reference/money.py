# 1-21 第①圈：熊的金額工具（正確版）。main.py 用 from money import fmt, total 拿這裡的函式。


def total(amounts):
    return sum(amounts)


def fmt(amount):
    return f"{amount:,} 元"


if __name__ == "__main__":
    assert total([120, 85]) == 205
    assert fmt(1250) == "1,250 元"
    print("money.py 自己的檢查都過了")
