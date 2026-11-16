# 1-19 第③圈 壞版本 2（課程準備的 AI 版本，範例示意）：門檻寫死成 300，用關鍵字給的 limit 沒有用到


def over_limit(amounts, limit=300):
    """挑出超過門檻的金額。"""
    result = []
    for a in amounts:
        if a > 300:
            result.append(a)
    return result
