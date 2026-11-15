# 1-14 正確版：分類小工具（課程寫好的函式，學員只呼叫、不用看懂 def 那一行，1-18 才教）
# 需求卡：both_months(nov, dec) 交回兩個月都有花錢的分類。nov、dec 是兩個月每一筆帳的分類（同一個分類會出現好幾次）；
#         交回的每個分類只出現一次，而且排好序（用 sorted 排，交回 list）。


def both_months(nov, dec):
    return sorted(set(nov) & set(dec))
