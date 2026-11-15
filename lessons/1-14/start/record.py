# 1-14 第①圈：一筆帳（tuple）拆成三個名字
# record 是一筆帳：日期、項目、金額，用圓括號包起來（tuple）。照下面兩步寫：
#   1. 用一行拆包，把 record 拆成 date、item、amount 三個名字
#   2. 印出「11/03 午餐 120 元」：print 裡放 date、item、amount，最後是 "元"
# check 會把 record 換成別的一筆再跑一次，所以要用拆包拿，不要把答案直接寫進 print。
record = ("11/03", "午餐", 120)

