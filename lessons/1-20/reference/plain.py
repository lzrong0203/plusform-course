# 1-20 第①圈的正確版：AI 的 5 行改寫成不用 lambda、不用 any／all 的普通寫法，每一個都用 assert 確認一樣。

entries = [("11/03", "餐", 120), ("11/01", "書", 450), ("11/02", "車", 30), ("11/04", "餐", 85)]

# ---- AI 寫的 5 行（不要改）----
by_amount = sorted(entries, key=lambda e: e[2])
newest = sorted(entries, key=lambda e: e[0], reverse=True)
top2 = sorted(entries, key=lambda e: e[2], reverse=True)[:2]
has_big = any(e[2] >= 300 for e in entries)
all_small = all(e[2] < 400 for e in entries)


# ---- 改寫 ----
def amount_of(e):
    return e[2]


def date_of(e):
    return e[0]


by_amount2 = sorted(entries, key=amount_of)
assert by_amount2 == by_amount

newest2 = sorted(entries, key=date_of, reverse=True)
assert newest2 == newest

top2b = sorted(entries, key=amount_of, reverse=True)[:2]
assert top2b == top2

has_big2 = False
for e in entries:
    if e[2] >= 300:
        has_big2 = True
assert has_big2 == has_big

all_small2 = True
for e in entries:
    if not e[2] < 400:
        all_small2 = False
assert all_small2 == all_small

print(by_amount2 == by_amount, newest2 == newest, top2b == top2, has_big2 == has_big, all_small2 == all_small)
