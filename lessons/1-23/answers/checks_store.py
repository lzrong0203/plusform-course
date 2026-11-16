# 1-23 第③圈：老師的標準檢查（validate 用）
from pathlib import Path

from store import load_entries, save_entries

TEST = Path(__file__).parent / "roundtrip_test.txt"


def roundtrip(entries):
    save_entries(TEST, entries)
    return load_entries(TEST)


a = [("11/03", "午餐", 120, "跟同事")]
assert roundtrip(a) == a
b = [("11/03", "午餐", 120, "跟同事"), ("11/04", "公車", 15, "")]
assert roundtrip(b) == b
assert roundtrip([]) == []
c = [("11/05", "聚餐", 600, "跟小明, 小華")]
assert roundtrip(c) == c   # 已知會當掉：備註有逗號，切成五段；2-4 用 CSV 解決
