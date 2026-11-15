# 壞版本 1：每個人都付 total / people 四捨五入（round）。除得盡的時候對；除不盡的時候，加起來就不等於原金額。


def share(total, people, who):
    return round(total / people)
