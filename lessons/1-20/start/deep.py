# 1-20 選做加深（check 不檢查）：遞迴，函式裡呼叫自己。只要追得出巢狀清單的加總就好。
# 先不要跑，用眼睛追：最下面那一行會印出什麼？每呼叫一次 deep_sum，就開一個新的小框（1-18）。
# 追完再跑：uv run lessons/1-20/deep.py；答案和一步一步的追法在課程資料夾的 lessons/1-20/補充.md。


def deep_sum(x):
    s = 0
    for item in x:
        if type(item) == list:      # 這一格本身又是一個 list：交給 deep_sum 自己加，再加進來
            s = s + deep_sum(item)
        else:
            s = s + item
    return s


print(deep_sum([120, [85, 300], [[45]]]))
