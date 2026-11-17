# 矯正包練習：型別提示只是說明，Python 跑的時候不檢查（1-20）
# 先不要跑。在紙上寫下最後三行各印出什麼，寫好在帳本資料夾打 uv run lessons/1-C4/practice/p_hints.py 對答案。
# 想一想：-> int 寫在那裡，交回來的就一定是整數嗎？


def per_person(total: int, people: int) -> int:
    return total / people


print(per_person(300, 3))
print(per_person(100, 8))
print(per_person(10.5, 2))
