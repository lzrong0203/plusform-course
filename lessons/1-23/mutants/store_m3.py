"""帳本的存檔和讀檔（課程版本，凍結版：不要改它）。

一筆帳是 (日期, 項目, 金額, 備註)，例如 ("11/03", "午餐", 120, "跟同事")。
檔案裡一行一筆，欄位用逗號隔開。
"""


def save_entries(path, entries):
    """把 entries 存進 path（整個檔案重寫）。

    輸入：path 檔案路徑；entries 一串 (日期, 項目, 金額, 備註)
    輸出：沒有交回東西，寫進檔案
    例子：save_entries(p, [("11/03", "午餐", 120, "跟同事")]) 以後，檔案是一行 11/03,午餐,120,跟同事
    """
    if not entries:
        return
    with open(path, "w", encoding="utf-8") as f:
        for d, item, amount, note in entries:
            f.write(f"{d},{item},{amount},{note}\n")


def load_entries(path):
    """從 path 讀回一串 (日期, 項目, 金額, 備註)，金額是整數。

    輸入：path 檔案路徑
    輸出：一串 (日期, 項目, 金額, 備註)
    例子：load_entries(p) 是 [("11/03", "午餐", 120, "跟同事")]
    """
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            d, item, amount, note = line.rstrip("\n").split(",")
            entries.append((d, item, int(amount), note))
    return entries
