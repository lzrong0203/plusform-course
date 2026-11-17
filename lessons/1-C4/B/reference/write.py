# 檢核站 4 卷 B 第三部分的參考答案：with open 一行一行讀（encoding="utf-8"），拿掉最後的換行、用逗號切開，金額變成整數加進 total；
# 最後一行後面沒有換行也一樣（rstrip 沒東西可拿就不拿）；空的檔案 for 一圈都不跑，交回 0
from pathlib import Path


def pay_total(path):
    """把付款紀錄檔裡每一筆的金額加起來。

    輸入：path，付款紀錄檔的位置。每一行是 日期,付款方式,金額（例如 11/03,現金,65）。
    輸出：所有金額加起來的整數。空的檔案交回 0。
    例子：檔案有 11/03,現金,65 和 11/04,悠遊卡,25 兩行，pay_total(那個檔) 是 90。
    """
    total = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = line.rstrip("\n")
            d, way, amount = row.split(",")
            total += int(amount)
    return total


if __name__ == "__main__":
    print(pay_total(Path(__file__).parent / "sample.txt"))
