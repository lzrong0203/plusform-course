# 矯正包練習：分帳的零頭（1-4）
# 先不要跑。在紙上寫下這支印出什麼。每人先付的要是整數元，零頭是除完剩下的幾元。
# 再用 uv run lessons/1-12/practice/p_split.py 跑，對答案；把算錯的那一行修好，要印出「每人 250 元，零頭 3 元」。
total = 1003
people = 4
each = total / people
left = total % people
print("每人", each, "元，零頭", left, "元")
