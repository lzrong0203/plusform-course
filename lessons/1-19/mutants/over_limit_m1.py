# 1-19 第③圈 壞版本 1（課程準備的 AI 版本，範例示意）：結果存在函式外面的 list（偷用全域變數存東西）
# 第一次呼叫是對的；跑完 result 不會清掉，第二次呼叫從上一次的結果接着加。

result = []


def over_limit(amounts, limit=300):
    """挑出超過門檻的金額。"""
    for a in amounts:
        if a > limit:
            result.append(a)
    return result
