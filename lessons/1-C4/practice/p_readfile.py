# 矯正包練習：寫一個讀檔加總的函式（1-23、1-18）
# 下面先寫好三個練習檔（跟這個檔放在一起）：三筆的、兩筆而且最後一行後面沒有換行的、空的。
# 寫好 sum_file：with open(path, encoding="utf-8") 一行一行讀，拿掉換行、用逗號切開，金額變成整數加進 total，最後 return total。
# 寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_readfile.py，要印出：315 135 0
from pathlib import Path

here = Path(__file__).parent
files = {"p_a.txt": "11/03,午餐,120\n11/04,公車,15\n11/05,晚餐,180\n", "p_b.txt": "11/03,午餐,120\n11/04,公車,15", "p_c.txt": ""}
for name in files:
    with open(here / name, "w", encoding="utf-8") as f:
        f.write(files[name])


def sum_file(path):
    """把帳本檔案每一行（日期,項目,金額）的金額加起來，交回整數；空的檔案交回 0。"""


print(sum_file(here / "p_a.txt"), sum_file(here / "p_b.txt"), sum_file(here / "p_c.txt"))
