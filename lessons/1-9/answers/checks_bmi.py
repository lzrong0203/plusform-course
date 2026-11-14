# 1-9 第③圈的參考答案（老師端也用它驗證壞版本）
from bmi import bmi_level

assert bmi_level(16) == "體重過輕"
assert bmi_level(18.5) == "健康體重"
assert bmi_level(22) == "健康體重"
assert bmi_level(24) == "體重過重"
assert bmi_level(26) == "體重過重"
assert bmi_level(27) == "肥胖"
assert bmi_level(30) == "肥胖"
