# 1-19 第③圈：需求寫進 docstring，函式內容交給 AI（或用凍結版），用測試驗收
#   1. 在 def 下面的 docstring 寫清楚三件事：輸入：、輸出：、例子：（例子寫一次真的呼叫，例如 over_limit([...]) 是 [...]）
#   2. 在 checks_over_limit.py 寫 assert（至少 3 條）
#   3. 把 def 那一行、docstring 和你的 assert 一起貼給 AI，請它照 docstring 寫函式內容（assert 不要改）；
#      沒有 AI 帳號的，打開課程資料夾的 lessons/1-19/frozen/over_limit.py，把 docstring 下面的函式內容抄過來
#   4. 在帳本資料夾跑 uv run lessons/1-19/checks_over_limit.py，什麼都沒印出來，代表每一條都成立
# 還沒有函式內容時也能跑：只有 docstring 的函式，交回的是 None（assert 會不成立）。


def over_limit(amounts, limit=300):
    """挑出超過門檻的金額。

    輸入：
    輸出：
    例子：
    """
