# 1-19 第③圈 壞版本 3（課程準備的 AI 版本，範例示意）：都沒超過的時候交回 None，不是空的 list


def over_limit(amounts, limit=300):
    """挑出超過門檻的金額。"""
    result = []
    for a in amounts:
        if a > limit:
            result.append(a)
    if len(result) == 0:
        return None
    return result
