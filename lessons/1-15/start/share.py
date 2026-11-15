# 1-15 正確版：占比小工具（課程寫好的函式，學員只呼叫、不用看懂 def 那一行，1-18 才教）
# 需求卡：shares(totals) 交回各分類的占比。totals 是各分類的小計（dict：分類 → 金額）；
#         每一類＝小計 ÷ 全部 × 100，用 round 留到小數一位；每個分類都要有（花 0 元的是 0.0）；不能動到原本的 totals；
#         各分類的占比加總要顯示 100%。


def shares(totals):
    whole = sum(totals.values())
    result = {}
    for kind, amount in totals.items():
        result[kind] = round(amount / whole * 100, 1)
    return result
