# 矯正包練習：TypeError，字串和數字不能直接相加（1-6、1-7）
# 這支會當掉。先在帳本資料夾打 uv run lessons/1-C2/practice/p_type_error.py 跑一次，這一筆打 40。
# 錯誤訊息從最下面一行看起：它說哪兩種東西不能一起算？往上看是第幾行？
# 錯誤出現的那一行，不一定是要改的那一行：這一筆的錢是哪一行拿到的？修好再跑，要印出 一共花了 120 元。
spent = 80
price = input("這一筆：")
spent = spent + price
print("一共花了", spent, "元")
