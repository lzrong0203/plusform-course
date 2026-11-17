# 矯正包練習：光禿禿的 except 什麼錯都接，連打錯字也接住（1-22）
# 下面第 10 行把 text 打錯成 txet。先不要跑，在紙上寫下：
#   1. 現在跑，最後一行印出什麼？
#   2. 把第 11 行的 except: 改成 except ValueError:，再跑，會怎樣？
# 寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_broad.py，兩種都跑跑看，對答案。


def to_yuan(text):
    try:
        return int(txet)
    except:
        return 0


print(to_yuan("120"), to_yuan("80"))
