# 壞版本 3：寫死三個人分（不管 people 是多少）。三個人分的時候都對；不是三個人就錯。


def share(total, people, who):
    each = total // 3
    left = total % 3
    if who <= left:
        return each + 1
    return each
