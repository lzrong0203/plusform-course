# 矯正包練習：count 加 1 要放在 break、continue 的下面，真的記了一筆才加（1-10）
# 先不要跑。在紙上寫下：依序打 30、直接按 Enter、40、q，這支會印出一共幾筆？應該是幾筆？
# 再用 uv run lessons/1-12/practice/p_count.py 照著打，對答案。
# 修好它：把 count = count + 1 搬到對的地方，再照著打一次，要印出「一共 2 筆」。
count = 0
while True:
    text = input("金額，打 q 結束：")
    count = count + 1
    if text == "q":
        break
    if text == "":
        continue
print("一共", count, "筆")
