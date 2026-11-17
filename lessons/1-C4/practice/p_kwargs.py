# 矯正包練習：預設值和關鍵字參數（1-19）
# 先不要跑。在紙上寫下最後四行各印出什麼，寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_kwargs.py 對答案。
# 提示：沒給的參數用預設值；用名字給的（people=2）不管寫在哪裡，都交給那個名字。


def price(amount, tip=10, people=1):
    return (amount + tip) // people


print(price(90))
print(price(90, people=2))
print(price(90, 0))
print(price(90, people=4, tip=30))
