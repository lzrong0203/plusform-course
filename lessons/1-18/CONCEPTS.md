# 1-18 用到的概念

這課的示範、起點檔、正確版（`reference/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-18 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別（含 None：1-3 教過）
- 數字運算
- 函式呼叫（len、sum）
- 比較與邏輯（含 assert）
- if
- for
- list（1-13 教過：append、pop）
- tuple 與 set（1-14 教過拆包：for kind, amount in entries 的 kind, amount）
- dict（1-15 教過：get(鍵, 0)、用鍵放值）
- 模組與 import（例外：只有 checks_by_category.py 的 from by_category import by_category 這一行，照抄就好；1-21 才教）
- 函式定義（這課教：def、參數、return、docstring；沒有 return 交回 None；list 交進函式，函式裡改盒子裡面，外面看得到）

`predict.txt`、`names_quiz.txt`、`tutor.md`、`docstring.md` 是文字檔，不是程式，不在檢查範圍。
`frozen/by_category.py` 是課程的凍結版（第③圈 AI 照 docstring 寫的版本，給沒有 AI 帳號的學員抄函式內容），不是起點檔。
