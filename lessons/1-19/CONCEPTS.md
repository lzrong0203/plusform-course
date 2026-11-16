# 1-19 用到的概念

這課的示範、起點檔、正確版（`reference/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-19 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別（含 None：1-3 教過）
- 數字運算
- 函式呼叫（len、sum）
- 比較與邏輯（含 assert；is：1-16 教過，這課用在 book is None）
- if
- for
- list（1-13 教過：append、索引）
- tuple 與 set（1-14 教過拆包：for kind, amount in entries 的 kind, amount）
- dict（1-15 教過：get(鍵, 0)、用鍵放值）
- 模組與 import（例外：只有 checks_over_limit.py 的 from over_limit import over_limit 這一行，照抄就好；1-21 才教）
- 函式定義（1-18 教過：def、參數、return、docstring）
- 預設值與關鍵字參數（這課教：def f(x, limit=300)、呼叫時寫 limit=100；預設值只在 def 那一行做一次，預設值寫 [] 會被每次呼叫共用，改成 None；函式裡給值的名字是區域變數，外面的是全域變數）

`scope.txt`、`tutor.md` 是文字檔，不是程式，不在檢查範圍。
`frozen/over_limit.py` 是課程的凍結版（第③圈 AI 照 docstring 寫的版本，給沒有 AI 帳號的學員抄函式內容），不是起點檔。
`start/add_entry.py` 故意寫成預設值用 [] 的陷阱（學員要改成 None），`start/report_long.py` 是拆成函式之前的長版本（給學員對照，不用改）。
