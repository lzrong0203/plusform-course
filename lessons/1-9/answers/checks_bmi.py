# 1-9 第③圈的參考答案（老師端也用它驗證壞版本）
from bmi import bmi_level

assert bmi_level(16) == "過輕"
assert bmi_level(18.5) == "正常"
assert bmi_level(22) == "正常"
assert bmi_level(24) == "過重"
assert bmi_level(26) == "過重"
assert bmi_level(30) == "肥胖"
