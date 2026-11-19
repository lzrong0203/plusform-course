# 第 1 級的寫法（1-8）：assert 一條一條寫在最外層，用 uv run 跑這個檔
from split import split

assert split(300, 3) == [100, 100, 100]
assert split(100, 3) == [34, 33, 33]
assert split(100, 4) == [25, 25, 25, 25]
