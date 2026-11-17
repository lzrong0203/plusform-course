# 1-27 第一部分：拼圖的參考排法（排法不只一種，check 照跑出來的結果判）
def add_up(texts):
    total = 0
    bad = 0
    for t in texts:
        try:
            total = total + int(t)
        except ValueError:
            bad = bad + 1
    return total, bad
s, n = add_up(["120", "abc", "80"])
print(f"合計 {s} 元，看不懂 {n} 筆")
