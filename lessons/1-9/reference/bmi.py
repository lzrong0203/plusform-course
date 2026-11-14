# 1-9 正確版：成人 BMI 分級（課程凍結的版本；學員只呼叫、不用看懂 def 那一行，1-18 才教）
# 照衛生福利部國民健康署〈成人健康體位標準〉：BMI＜18.5 體重過輕、18.5≤BMI＜24 健康體重、24≤BMI＜27 體重過重、BMI≥27 肥胖。
# 本課只用來練程式，不是健康建議。


def bmi_level(bmi):
    if bmi >= 27:
        return "肥胖"
    elif bmi >= 24:
        return "體重過重"
    elif bmi >= 18.5:
        return "健康體重"
    else:
        return "體重過輕"
