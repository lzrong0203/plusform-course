# 1-21 用到的概念

這課的示範、起點檔、正確版（`reference/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-21 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（1-5 教過：f-string 的 {amount:,} 千分位）
- 函式呼叫（sum）
- 比較與邏輯（含 assert）
- if
- list
- 函式定義（1-18 教過：def、參數、return）
- 模組與 import（這課教：一個 .py 檔就是一個模組；from money import fmt, total、import math 兩種寫法；import 會把那個檔從頭跑一遍；__name__ 和 if __name__ == "__main__":；標準函式庫的 datetime（date.today、strftime、strptime）、random、math、pathlib；ModuleNotFoundError 與查 PyPI）
- class（例外：只有 strptime 交回的日期用 d.month、d.day 拿月和日這一處，看得懂就好；物件的屬性 1-24 才教）

`docs.txt`、`imports.txt`、`tutor.md` 是文字檔，不是程式，不在檢查範圍。
