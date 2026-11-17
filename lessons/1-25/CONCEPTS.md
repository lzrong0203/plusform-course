# 1-25 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-25 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（1-5 教過；這課沒有新的字串寫法，d.replace(…) 是日期的 replace，ast 粗略檢查分不出來）
- 函式呼叫（min）
- 比較與邏輯（含 assert）
- if
- list（1-13 教過：calendar.monthrange(…)[1] 拿第二個值）
- tuple 與 set（1-14 教過：year, month = …）
- 函式定義（1-18 教過：def、參數、return）
- 預設值與關鍵字參數（1-19 教過：d.replace(month=…) 用關鍵字交參數）
- 例外處理（1-22 教過：壞版本 m1 用 try／except ValueError）
- 模組與 import（1-21 教過：import settings、from dates import next_month、標準函式庫 datetime 的 date；修正版用了 calendar.monthrange，查官方文件看得懂就好）
- class（1-24 教過：d.year、d.month、d.day 這種屬性；settings.PAY_DAY = 31 是改另一個模組裡的名字）

這課新教的不是 Python 語法，是 VS Code 的工具：debugger（中斷點、F5、F10、F11、變數面板、呼叫堆疊）、Go to Definition（移至定義）、Find All References（尋找所有參考），和 Markdown。
`debug.txt`、`ask.txt`、`tutor.md`、`bug_report.md` 是文字檔，不是程式，不在檢查範圍。
`dates_fixed.py`（起點檔）是課程的修正版：學員不改它，第③圈用 assert 驗收。
