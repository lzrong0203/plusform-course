# 矯正包練習：input 交回的一定是字串；打 q 的那一次，也會被交給 int()（1-6、1-10）
# 先在帳本資料夾打 uv run lessons/1-12/practice/p_q.py，打 20、30、q，看看打 q 的時候怎麼了。
# 錯誤訊息的最後一行說什麼？引號裡的值是程式實際拿到的東西。
# 修好它：先看是不是 q、要停就 break，再交給 int()。打 20、30、q，要印出「一共 50 元」。
total = 0
while True:
    amount = int(input("金額，打 q 結束："))
    if amount == "q":
        break
    total = total + amount
print("一共", total, "元")
