# 1-22 第②圈：AI 的建議（範例示意）：用一個光禿禿的 except: 把所有錯誤都接住。
# 跑跑看：uv run lessons/1-22/ai_bare.py，在「金額：」後面按 Control C（Mac 和 Windows 都一樣）想停下來，看看會怎樣。
# 停不下來的話，打一個正常的金額（例如 120）再按 Enter，迴圈就會結束。這個檔不檢查。
from money import to_yuan

while True:
    try:
        text = input("金額：")
        amount = to_yuan(text)
        print("記下", amount, "元")
        break
    except:
        print("請再輸入一次")
