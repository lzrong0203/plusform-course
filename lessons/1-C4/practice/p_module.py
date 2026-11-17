# 矯正包練習：import 會把那個檔從頭跑一遍；if __name__ == "__main__": 底下的，只有直接跑這個檔才跑（1-21）
# 先不要跑。在紙上寫下兩個答案：
#   1. 在帳本資料夾打 uv run lessons/1-C4/practice/p_module.py，印出哪幾行？
#   2. 先打 cd lessons/1-C4/practice 走進這個資料夾，再打 uv run python -c "import p_module"，印出哪幾行？
# 寫好照著打這兩個指令，對答案。


def double(n: int) -> int:
    return n * 2


print("載入 p_module，__name__ 是", __name__)
if __name__ == "__main__":
    print("直接跑才會印：", double(21))
