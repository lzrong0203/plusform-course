# 1-23 第③圈：存了再讀回來，要一模一樣（來回測試）
# store.py 是課程版本（凍結版，不要改它）：一筆帳是 (日期, 項目, 金額, 備註)，檔案裡一行一筆、欄位用逗號隔開。
# 每一條檢查都長這樣：先寫好一串帳，再 assert roundtrip(那一串) == 那一串
from pathlib import Path

from store import load_entries, save_entries

TEST = Path(__file__).parent / "roundtrip_test.txt"   # 測試用的檔案，不是你的 ledger.txt


def roundtrip(entries):
    """存進測試檔，再讀回來。"""
    save_entries(TEST, entries)
    return load_entries(TEST)


a = [("11/03", "午餐", 120, "跟同事")]
assert roundtrip(a) == a

# 換你寫：至少再兩條。想想哪些帳最容易存壞：好幾筆？空的帳本？
# 最後再寫一條：備註裡有逗號（例如 "跟小明, 小華"）。跑跑看會怎樣，再照 README 記下來。
