# 壞版本 2：零頭全部給第 1 個人付。零頭只有 0 或 1 元的時候對；零頭 2 元以上，第 1 個人會比別人多付 2 元。


def share(total, people, who):
    each = total // people
    left = total % people
    if who == 1:
        return each + left
    return each
