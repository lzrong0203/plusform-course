entries = [("11/03", 120), ("11/01", 450), ("11/02", 30)]
short = sorted(entries, key=lambda e: e[1], reverse=True)


plain = sorted(entries, key=amount_of, reverse=True)

print(plain)


# 1-20 影片裡熊的示範檔（跟著打，不檢查）：第 3、4 行打 def amount_of(e): 和 return e[1]，第 6 行打 assert short == plain，
# 存檔以後在帳本資料夾打 uv run lessons/1-20/sort.py。第 3、4 行還沒打之前跑，會出現 NameError（amount_of 還沒有定義）。
