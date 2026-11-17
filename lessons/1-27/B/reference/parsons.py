# 1-27 第一部分（卷 B）：拼圖的參考排法（排法不只一種，check 照跑出來的結果判）
def biggest_ok(texts):
    best = 0
    bad = 0
    for t in texts:
        try:
            best = max(best, int(t))
        except ValueError:
            bad = bad + 1
    return best, bad
m, n = biggest_ok(["45", "?", "300", "八十"])
print(f"最大 {m} 元，看不懂 {n} 筆")
