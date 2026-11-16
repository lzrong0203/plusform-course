# 1-19 第③圈的凍結版：影片裡 AI（Claude 網頁版的一般聊天，示範帳號，2026-11-16）照同一份 docstring 和 assert 寫的函式，原樣保存、之後不再改。
# AI 只交回函式（沒有附上 docstring）；這裡把熊的 docstring 放回 def 下面，函式內容是 AI 寫的原樣（result = [] 到 return result）。
# 沒有 AI 帳號的同學：把 docstring 下面的函式內容抄進你帳本的 lessons/1-19/over_limit.py（docstring 留你自己寫的）。


def over_limit(amounts, limit=300):
    """挑出超過門檻的金額。

    輸入：amounts 是一串金額；limit 是門檻，沒給就是 300
    輸出：新的 list，照原本的順序；都沒超過交回 []
    例子：over_limit([120, 450, 85]) 是 [450]
          over_limit([120, 450, 85], limit=100) 是 [120, 450]
    """
    result = []
    for amount in amounts:
        if amount > limit:
            result.append(amount)
    return result
