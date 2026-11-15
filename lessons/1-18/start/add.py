# 1-18 第①圈：把一筆加進帳本
# 在這幾行註解下面，寫一個函式 add_entry(book, amount)：把 amount 加到 book 的最後面（用 append）。
# 這個函式不用 return。最下面四行不要改：呼叫兩次，再印出 nov。
# 想一想：add_entry 沒有 return，為什麼外面的 nov 也多了兩筆？（提示：1-16 的名牌和盒子）
# check 會跑這支程式，也會把 nov 換成別的帳本，再跑一次。



nov = [120, 85]
add_entry(nov, 300)
add_entry(nov, 45)
print(nov)
