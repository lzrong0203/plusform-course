# 1-4 第③圈：課程的正確版分帳機（AI 照需求卡寫的，課程凍結的版本）
# 一筆錢三個人分，交回三個人各付多少。你不用看懂這裡的寫法（def、return 之後的課會教），用 cases.txt 驗收它就好。
def split3(total):
    each = total // 3                  # 每人先付的整數元（// 往比較小的那邊取整數）
    left = total % 3                   # 零頭：一定是 0、1 或 2 元
    first = each + (left + 1) // 2     # 零頭有 1 元以上，第一個人多付 1 元
    second = each + left // 2          # 零頭有 2 元，第二個人也多付 1 元
    third = total - first - second     # 剩下的給第三個人，三個人加起來一定等於 total
    return first, second, third
