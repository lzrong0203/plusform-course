# 矯正包練習：預算燈號，剛好在邊界上的那幾個（1-8、1-9）
# 規則：低於預算的 80% 綠燈；80% 到 100%（剛好 100% 也算）黃燈；超過預算紅燈。
# 先不要跑。在紙上寫下 total 是 790、800、1000、1001 的時候，這支各印出什麼？哪幾個跟規則不一樣？
# 一次改一個 total = 後面的數字，存檔再用 uv run lessons/1-12/practice/p_light.py 跑，對答案；再把比較修好，四個都要對。
budget = 1000
total = 800
if total <= budget * 0.8:
    print("綠燈")
elif total < budget:
    print("黃燈")
else:
    print("紅燈")
