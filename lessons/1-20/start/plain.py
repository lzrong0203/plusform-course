# 1-20 第①圈：把 AI 常寫的 5 行，改寫成不用 lambda、不用 any／all 的普通寫法，再用 assert 確認結果一樣。
# entries 那一行和 AI 寫的 5 行不要改（check 會把 entries 換成別的資料，再跑一次）。最後一行 print 也不要改。
# 寫法：
#   - 有 lambda 的：先用 def 寫一個函式（例如 amount_of），key 交那個函式的名字
#   - any／all：改回 for 迴圈，先給 False（或 True），遇到符合的再改
#   - 每改好一個，下面寫一條 assert，確認跟 AI 寫的一樣
# 寫完在帳本資料夾跑：uv run lessons/1-20/plain.py，最後印出 True True True True True 就對了。

entries = [("11/03", "餐", 120), ("11/01", "書", 450), ("11/02", "車", 30), ("11/04", "餐", 85)]

# ---- AI 寫的 5 行（不要改）----
by_amount = sorted(entries, key=lambda e: e[2])
newest = sorted(entries, key=lambda e: e[0], reverse=True)
top2 = sorted(entries, key=lambda e: e[2], reverse=True)[:2]
has_big = any(e[2] >= 300 for e in entries)
all_small = all(e[2] < 400 for e in entries)


# ---- 你的改寫（名字後面加 2；top2 的改寫叫 top2b）----
# 範例（第一行已經改好了）：
def amount_of(e):
    return e[2]


by_amount2 = sorted(entries, key=amount_of)
assert by_amount2 == by_amount

# 換你改：newest2、top2b、has_big2、all_small2，每個下面寫一條 assert


# ---- 最後一行不要改：五個都跟 AI 寫的一樣，就印出五個 True ----
print(by_amount2 == by_amount, newest2 == newest, top2b == top2, has_big2 == has_big, all_small2 == all_small)
