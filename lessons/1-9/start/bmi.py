# 1-9 第③圈用的 bmi_level()：課程版本，不用改，也不用看懂 def 那一行（1-18 才教）。
#
# 它照衛生福利部國民健康署〈成人健康體位標準〉，交回成人 BMI 的分級（本課只用來練程式，不是健康建議）：
#   BMI 小於 18.5              → 體重過輕
#   18.5 以上、小於 24         → 健康體重
#   24 以上、小於 27           → 體重過重
#   27 以上                    → 肥胖
#
# 你在 checks_bmi.py 寫的 assert，會在你的電腦上呼叫這一份（它是正確版）。
# check.py 判分的時候，會拿課程的正確版和 3 個藏起來的壞版本，各跑一次你的 assert。


def bmi_level(bmi):
    if bmi >= 27:
        return "肥胖"
    elif bmi >= 24:
        return "體重過重"
    elif bmi >= 18.5:
        return "健康體重"
    else:
        return "體重過輕"
