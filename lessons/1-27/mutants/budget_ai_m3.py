# 1-27 第三部分　壞版本 3（範例示意）：交回的是整數，存進 budgets 的卻是字串（"8000"）


def set_budget(budgets: dict, month: str, text: str) -> int:
    """設定某個月的預算，記進 budgets（{月份: 預算}），交回設定好的金額。

    輸入：budgets 是一個 dict；month 寫成「年-月」，例如 "2026-11"；text 是打進來的金額，例如 "8,000元"
    輸出：設定好的預算（整數）
    規則：月份要像 2026-11（四位數的年、兩位數的月），月要在 01 到 12；金額拿掉逗號和「元」以後要大於 0；
          不合法就 raise ValueError，budgets 不能被改到；同一個月再設一次，蓋掉舊的
    例子：set_budget(b, "2026-11", "8,000元") 交回 8000，b 變成 {"2026-11": 8000}
    """
    parts = month.split("-")
    if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2 or not (parts[0] + parts[1]).isdigit():
        raise ValueError(f"月份要寫成像 2026-11：{month}")
    if not 1 <= int(parts[1]) <= 12:
        raise ValueError(f"月要在 01 到 12：{month}")
    amount = int(text.replace(",", "").replace("元", ""))
    if amount <= 0:
        raise ValueError(f"預算要大於 0：{text}")
    budgets[month] = text.replace(",", "").replace("元", "")
    return amount
