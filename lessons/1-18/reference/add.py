# 1-18 第①圈：把一筆加進帳本（正確版）


def add_entry(book, amount):
    book.append(amount)


nov = [120, 85]
add_entry(nov, 300)
add_entry(nov, 45)
print(nov)
