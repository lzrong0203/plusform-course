# 1-19 第①圈：add_entry 的正確版（預設值寫 None，函式裡才做新的 list；官方教學 4.9.1 的寫法）


def add_entry(amount, book=None):
    if book is None:
        book = []
    book.append(amount)
    return book


nov = add_entry(120)
dec = add_entry(65)
print(nov, dec)
