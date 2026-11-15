# Lv1 上關卡　第三部分：課程的正確版分帳（AI 照需求卡寫的，課程凍結的版本）
# share(total, people, who)：total 元給 people 個人分，交回第 who 個人（從 1 數起）要付多少。
# 你不用看懂這裡的寫法（def、return 之後的課會教），也不用改它：用 checks_share.py 的 assert 驗收它就好。


def share(total, people, who):
    each = total // people        # 每人先付的整數元
    left = total % people         # 零頭：除不盡剩下的幾元
    if who <= left:               # 零頭由前面的人各多付 1 元
        return each + 1
    return each
