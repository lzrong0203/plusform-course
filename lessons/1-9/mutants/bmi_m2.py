# 1-9 壞版本 2


def bmi_level(bmi):
    if bmi >= 27:
        return "肥胖"
    elif bmi >= 24:
        return "體重過重"
    elif bmi > 18.5:
        return "健康體重"
    else:
        return "體重過輕"
