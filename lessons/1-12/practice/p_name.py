# 矯正包練習：NameError，這個名字還沒有；要改的可能在別的地方（1-7）
# 先在帳本資料夾打 uv run lessons/1-12/practice/p_name.py。
# 錯誤訊息最後一行說哪一個名字找不到？Python 猜你想打的是哪一個（Did you mean）？
# 往上找：這個名字應該在哪一行設好？修好以後，要印出「一共 6 杯」。
cup = 0
for day in range(3):
    cups = cups + 2
print("一共", cups, "杯")
