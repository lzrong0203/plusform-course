# 1-18 第③圈：需求寫進 docstring，函式內容交給 AI（或用凍結版），用測試驗收
#   1. 在 def 下面的 docstring 寫清楚三件事：輸入：、輸出：、例子：（例子寫一次真的呼叫，例如 by_category([...]) 是 {...}）
#   2. 在 checks_by_category.py 寫 assert（至少 3 條，要有一條交空的 list 進去）
#   3. 把 def 那一行、docstring 和你的 assert 一起貼給 AI，請它照 docstring 寫函式內容（assert 不要改）；
#      沒有 AI 帳號的，打開課程資料夾的 lessons/1-18/frozen/by_category.py，把 docstring 下面的函式內容抄過來
#   4. 在帳本資料夾跑 uv run lessons/1-18/checks_by_category.py，什麼都沒印出來，代表每一條都成立
# 還沒有函式內容時也能跑：只有 docstring 的函式，交回的是 None（assert 會不成立）。


def by_category(entries):
    """各分類的小計。

    輸入：
    輸出：
    例子：
    """
