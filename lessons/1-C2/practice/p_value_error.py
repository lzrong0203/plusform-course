# 矯正包練習：ValueError，int() 看不懂的字（1-5、1-6）
# 這支會當掉。先在帳本資料夾打 uv run lessons/1-C2/practice/p_value_error.py 跑一次，金額照打 1,200元。
# 錯誤訊息最下面一行，引號裡的值是程式實際拿到的東西：int() 看不懂裡面的哪些字？
# 用 replace 把看不懂的字拿掉（可以接兩次），修好再跑，要印出 一半是 600 元。
amount = int(input("金額："))
print("一半是", amount // 2, "元")
