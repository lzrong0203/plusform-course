# 2-3 第①圈：把 checks_split.py 的 assert 搬進來，每一條包成一個 def test_ 開頭的函式
# 跑法（在帳本資料夾）：uv run pytest
from split import split


def test_even():
    assert split(300, 3) == [100, 100, 100]


# 換你搬：checks_split.py 另外兩條（100 元三個人分、100 元四個人分）
