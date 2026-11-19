# 2-3 參考答案（老師的標準測試）：分帳六個案例用 parametrize，人數是 0 用 pytest.raises
import pytest

from split import split


@pytest.mark.parametrize("total, people, expected", [
    (300, 3, [100, 100, 100]),
    (100, 3, [34, 33, 33]),
    (101, 3, [34, 34, 33]),
    (100, 4, [25, 25, 25, 25]),
    (10, 4, [3, 3, 2, 2]),
    (1, 3, [1, 0, 0]),
])
def test_split(total, people, expected):
    assert split(total, people) == expected


def test_no_people():
    with pytest.raises(ValueError):
        split(100, 0)
