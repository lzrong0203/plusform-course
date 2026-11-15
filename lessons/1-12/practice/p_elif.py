# 矯正包練習：if、elif 沒有 else，都不成立就什麼都不做；enumerate 的編號從 start 開始（1-9、1-11）
# 先不要跑。在紙上寫下每一行印出什麼（有一圈什麼都不印）。
# 再用 uv run lessons/1-12/practice/p_elif.py 跑，對答案。
# 對了以後，把 start=1 拿掉，再寫一次、跑一次：編號從幾開始？
for i, cost in enumerate([90, 300, 150, 40], start=1):
    if cost > 250:
        print(i, "太貴了")
    elif cost >= 100:
        print(i, "還可以")
print("看完了")
