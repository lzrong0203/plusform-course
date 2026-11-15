# 矯正包練習：sort() 直接把 list 排好、交回 None；sorted() 交回排好的新 list、原本的不動（1-13）
# 先不要跑。在紙上寫下最後三行 print 各印出什麼，寫好再在帳本資料夾打 uv run lessons/1-C3/practice/p_sort.py，對答案。
nums = [300, 45, 120]
new = sorted(nums)
print(new, nums)
got = nums.sort()
print(got)
print(nums)
