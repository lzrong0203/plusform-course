# 檢核站 4　第三部分：手寫（4 題，關掉 AI，10 行左右寫得完）
# 寫好下面的 file_total：打開一個帳本檔案，把每一筆的金額加起來，用 return 交回。
# 帳本檔案每一行是一筆帳：日期,項目,金額（用逗號隔開，跟 1-23 的 ledger.txt 一樣），例如：
#   11/03,午餐,120
#   11/04,公車,15
# 做法：
#   1. def 那一行和 docstring 不要改，函式內容寫在 docstring 下面。
#   2. 打開檔案要用 with open(…, encoding="utf-8")（1-23）。
#   3. 對答案的時候，check 會自己寫好幾個帳本檔案交給 file_total：筆數不一樣、最後一行後面沒有換行、空的檔案都有，
#      每一個都要算對。所以要用算的，不要把答案寫死。
# 寫好存檔，在帳本資料夾打 uv run lessons/1-C4/write.py 跑跑看：最下面會拿旁邊的 sample.txt（三筆）來算，要印出 315。
from pathlib import Path


def file_total(path):
    """把帳本檔案裡每一筆的金額加起來。

    輸入：path，帳本檔案的位置。每一行是 日期,項目,金額（例如 11/03,午餐,120）。
    輸出：所有金額加起來的整數。空的檔案交回 0。
    例子：檔案有 11/03,午餐,120 和 11/04,公車,15 兩行，file_total(那個檔) 是 135。
    """


if __name__ == "__main__":
    print(file_total(Path(__file__).parent / "sample.txt"))
