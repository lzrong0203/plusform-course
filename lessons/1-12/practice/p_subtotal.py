# 矯正包練習：小計（1-9、1-11）
# 下面這支要算兩個小計：100 元以上的「大筆」、不到 100 元的「小筆」。現在印出來的不對。
# 先跑一次：uv run lessons/1-12/practice/p_subtotal.py，看看小筆和大筆各是多少。
# 想想：小計從 0 開始的那兩行，應該放在迴圈裡面還是外面？改好再跑，要印出「小筆 130 元」「大筆 300 元」。
for cost in [60, 200, 70, 100]:
    small = 0
    big = 0
    if cost >= 100:
        big = big + cost
    else:
        small = small + cost
print("小筆", small, "元")
print("大筆", big, "元")
