# 1-19 第③圈：挑出超過門檻的金額（正確版）


def over_limit(amounts, limit=300):
    """挑出超過門檻的金額。

    輸入：amounts 是一串金額；limit 是門檻，沒給就是 300
    輸出：新的 list，照原本的順序；都沒超過交回 []
    例子：over_limit([120, 450, 85]) 是 [450]
          over_limit([120, 450, 85], limit=100) 是 [120, 450]
    """
    result = []
    for a in amounts:
        if a > limit:
            result.append(a)
    return result
