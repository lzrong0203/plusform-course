# 2-4 用到的概念

這課的示範、起點檔、正確版（`reference/`）、壞版本、參考答案，只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 2-4 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算（民國年加 1911）
- 字串操作（`replace(",", "")`、`strip()`、`rstrip("\n")`、`split(",")`、f-string 的 `:02d`）
- 函式呼叫（`int(...)`、`len(...)`）
- 比較與邏輯（`if not row["交易日期"]`、`in`、assert）
- if
- while（`continue`：1-10 和迴圈一起教過）
- for（`for row in csv.DictReader(f)`、`continue`）
- list
- tuple 與 set（一筆帳 `(日期, 項目, 分類, 金額)`）
- dict（DictReader 的每一列、`settings`、`totals.get(category, 0)`）
- 函式定義
- 預設值與關鍵字參數（`encoding="utf-8"`、`newline=""`、`fieldnames=FIELDS`、`ensure_ascii=False`）
- 模組與 import（`import re`：Python 內建、照規則找字的模組，這課只要看得懂 `re.fullmatch` 那一行和 `\D`）
- 例外處理（`raise ValueError(...)`、`raise KeyError(...)`）
- 檔案讀寫（`with open(p, "w", encoding="utf-8", newline="")`、`Path(__file__).parent`）
- class（`m.group(1)`、`w.writeheader()`、`Path(__file__).parent` 這種物件和它的方法：1-24 教過）
- CSV 與 JSON（`csv.DictWriter`、`csv.DictReader`、`json.dump(…, ensure_ascii=False, indent=2)`、`json.load`、`json.loads`）

`re.txt` 是對答，`pandas.md`、`decision.md` 是自評的表單，都不是程式，不在檢查範圍。
`conftest.py` 是課程準備的空檔（讓 pytest 找得到同一個資料夾的 import_bank.py），不用改。
`bank_a.csv`、`bank_b.csv` 是課程準備的假資料（金額、店名都是編的），不是真的銀行匯出檔。
