# 1-19 第①圈：把 report_long.py（60 行）拆成五個小函式
# report_long.py 同樣的步驟寫了兩次（預算 1000、預算 1200）。下面已經寫好五個函式的名字和說明（docstring），
# 請把 report_long.py 裡對應的幾行搬進函式裡：前四個用 return 交回結果，report 只負責印（用前四個函式）。
# 最下面三行不要改。跑出來要跟 report_long.py 一模一樣，兩支都跑跑看：
#   uv run lessons/1-19/report_long.py
#   uv run lessons/1-19/split.py
# check 會跑這支程式，也會直接呼叫 total、by_category、biggest、light。


def total(entries):
    """合計。輸入：一串 (分類, 金額)。輸出：金額加起來。"""


def by_category(entries):
    """各分類的小計。輸入：一串 (分類, 金額)。輸出：dict，分類 → 合計。"""


def biggest(entries):
    """最大的一筆。輸入：一串 (分類, 金額)，至少一筆。輸出：金額最大的那一筆 (分類, 金額)。"""


def light(s, budget=1000):
    """預算燈號（1-9）。輸入：合計 s、預算 budget（沒給就是 1000）。輸出："綠燈"、"黃燈" 或 "紅燈"。"""


def report(entries, budget=1000):
    """印出一個月的報表，用上面四個函式。輸入：一串 (分類, 金額)、預算 budget（沒給就是 1000）。不交回東西。"""


nov = [("餐", 120), ("車", 30), ("餐", 85), ("書", 450), ("車", 60), ("餐", 300)]
report(nov)
report(nov, budget=1200)
