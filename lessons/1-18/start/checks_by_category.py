# 1-18 第③圈：替 by_category 寫測試（assert）
# 課程藏了 3 個 AI 寫錯的版本（範例示意）。你寫的 assert（至少 3 條）要做到：
#   在正確的版本上全部成立，在每一個寫錯的版本上，至少有一條不成立。
# 寫法：每一段先用一行註解（# 開頭）寫你要檢查什麼，下面再寫 assert。
# 寫完先在帳本資料夾跑一次：uv run lessons/1-18/checks_by_category.py
#   它用的是同一個資料夾裡你的 by_category.py。什麼都沒印出來，代表每一條都成立。
# 再回到課程資料夾打：uv run check.py 1-18

# 下面這一行是在說「要用 by_category.py 裡的 by_category」，要留著，不要刪掉
from by_category import by_category

# 範例（可以留著，算在 3 條裡）：同一類的兩筆要加起來
assert by_category([("餐", 120), ("餐", 85)]) == {"餐": 205}

# 換你寫（至少再 2 條，其中一條交空的 list 進去）：
