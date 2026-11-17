# 矯正包練習：最後一行後面不一定有換行（1-23）
# 下面先寫好一個兩行的檔，第二行後面沒有換行。先不要跑，在紙上寫下兩段 for 各印出哪兩行，
# 寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_lastline.py 對答案（repr 會把字串的引號一起印出來，看得出最後有沒有被切掉）。
# 想一想：哪一種寫法，最後一行的金額會被切掉一個字？
from pathlib import Path

p = Path(__file__).parent / "p_lastline.txt"
with open(p, "w", encoding="utf-8") as f:
    f.write("11/03,午餐,120\n11/04,公車,15")

with open(p, encoding="utf-8") as f:
    for line in f:
        print(repr(line[:-1]))
with open(p, encoding="utf-8") as f:
    for line in f:
        print(repr(line.rstrip("\n")))
