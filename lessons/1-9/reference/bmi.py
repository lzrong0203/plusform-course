# 1-9 正確版：BMI 分級（課程凍結的版本）


def bmi_level(bmi):
    if bmi >= 27:
        return "肥胖"
    elif bmi >= 24:
        return "過重"
    elif bmi >= 18.5:
        return "正常"
    else:
        return "過輕"
