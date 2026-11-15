# 矯正包練習：while 跑幾圈、continue 跳過這一圈下面的那幾行（1-10）
# 先不要跑。在紙上畫追蹤表（一圈一列：n 是多少、這一圈有沒有加進 total），寫下最後印出的兩個數字。
# 再用 uv run lessons/1-12/practice/p_while.py 跑，對答案。
# 對了以後，把 n % 3 的 3 改成 2，再寫一次、跑一次。
n = 0
total = 0
times = 0
while n < 7:
    n = n + 1
    if n % 3 == 0:
        continue
    total = total + n
    times = times + 1
print(total, times)
