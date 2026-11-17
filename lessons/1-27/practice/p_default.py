# 矯正包練習：預設值用 [] 的陷阱（1-19）
# 1. 先不要跑。在紙上寫下最後兩行各印出什麼，寫好在帳本資料夾打 uv run lessons/1-27/practice/p_default.py 對答案。
#    （預設值只在 Python 讀到 def 那一行時做一次，沒給 bag 的呼叫都共用同一個盒子。）
# 2. 照 1-19 官方教學的寫法改：預設值改成 None，函式裡 bag 是 None 的時候，才做一個新的空 list。
#    改好再跑，要印出 ['茶'] 和 ['麵包']。


def add_item(item, bag=[]):
    bag.append(item)
    return bag


print(add_item("茶"))
print(add_item("麵包"))
