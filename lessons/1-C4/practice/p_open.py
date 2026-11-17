# 矯正包練習：用 with open 打開檔案，一律寫 encoding="utf-8"（1-23）
# 下面先幫你寫好一個練習檔 p_open.txt（跟這個檔放在一起，兩行帳）。
# 在最下面「在這裡寫」那一行下面，用 with open(p, encoding="utf-8") as f: 一行一行讀，把每一行拿掉換行以後印出來。
# 寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_open.py，要印出：
#   11/03,午餐,120
#   11/04,公車,15
# 想一想：沒寫 encoding 的話，Windows 會用系統預設的編碼讀（台灣常見的是 cp950），UTF-8 存的中文會怎樣？（1-23 的 Windows 小卡）
from pathlib import Path

p = Path(__file__).parent / "p_open.txt"
with open(p, "w", encoding="utf-8") as f:
    f.write("11/03,午餐,120\n11/04,公車,15\n")

# 在這裡寫：
