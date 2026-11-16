# 1-20 第③圈：需求寫進 docstring，型別提示也寫好，函式內容交給 AI（或用凍結版），用測試驗收
#   1. def 那一行的型別提示已經寫好：entries 是一串 (分類, 金額)，交回一串 (分類, 合計)；不要刪掉
#   2. 在 def 下面的 docstring 寫清楚三件事：輸入：、輸出：、例子：（例子寫一次真的呼叫，例如 top3([...]) 是 [...]）
#   3. 在 checks_top3.py 寫 assert（至少 3 條）
#   4. 把 def 那一行、docstring 和你的 assert 一起貼給 AI，請它照 docstring 寫函式內容（assert 不要改）；
#      沒有 AI 帳號的，打開課程資料夾的 lessons/1-20/frozen/top3.py，把 docstring 下面的函式內容抄過來
#   5. 在帳本資料夾跑 uv run lessons/1-20/checks_top3.py，什麼都沒印出來，代表每一條都成立
# 還沒有函式內容時也能跑：只有 docstring 的函式，交回的是 None（assert 會不成立）。


def top3(entries: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """依分類加總，排出花費最大的前三類。

    輸入：
    輸出：
    例子：
    """
