# 1-9 第①圈：預算燈號
#
# 先輸入「這個月花了多少」，再輸入「預算是多少」，然後印出一個燈號：
#   花費低於預算的 80%          → 綠燈
#   80% 到 100%（剛好 100% 也算） → 黃燈
#   超過預算                    → 紅燈
#
# 輸入的部分已經寫好了，你只要寫最下面的 if／elif／else。
# 自己試跑（在帳本資料夾裡）：uv run lessons/1-9/budget_light.py

spent = int(input("這個月花了多少？"))
budget = int(input("預算是多少？"))
ratio = spent / budget  # ratio 是小數：花 800、預算 1000 時，ratio 是 0.8（不是 80）

# 在這裡寫你的 if／elif／else，每一條用 print 印出「綠燈」「黃燈」或「紅燈」
