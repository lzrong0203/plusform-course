# 1-9 壞版本 3


def bmi_level(bmi):
    if bmi >= 27:
        return "肥胖"
    elif bmi >= 18.5:
        return "正常"
    elif bmi >= 24:
        return "過重"
    else:
        return "過輕"
