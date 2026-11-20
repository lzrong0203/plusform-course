# 2-5 用到的概念

這課的示範、起點檔、正確版（`reference/`）、壞版本、參考答案，只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 2-5 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 數字運算（`+`：`month + "%"`、`totals.get(...) + int(...)`）
- 資料型別（`None`：金額空白存成 NULL，Python 讀出來是 None）
- 字串操作（`startswith`、f-string（第①圈故意拿它拼 SQL，示範為什麼不行）、`month + "%"`）
- 函式呼叫（`int(...)`）
- 比較與邏輯（`if not row["金額"]`、assert）
- while（`continue`：1-10 和迴圈一起教過）
- if（`int(row["金額"]) if row["金額"] else None`）
- for
- list
- 推導式與 zip（`run_sql.py` 的 `" | ".join(c[0] for c in …)`：課程準備的小工具）
- tuple 與 set（交給 execute 的值 `(d, item, cat, amount, note)`）
- dict（`totals.get(...)`、DictReader 的每一列）
- 函式定義
- 預設值與關鍵字參數（`encoding="utf-8"`、`newline=""`、`missing_ok=True`）
- 模組與 import（`run_sql.py` 用 `sys.argv` 拿檔名：課程準備的小工具，學員不用改）
- 檔案讀寫（`with open(...)`、`Path(__file__).parent`、`read_text`）
- class（`con.execute(...)`、`cur.fetchall()` 這種物件和它的方法：1-24 教過）
- CSV 與 JSON（`csv.DictReader`）
- SQLite（`sqlite3.connect`、`execute` 用問號交值、`commit`、`complete_statement`；SQL 的 CREATE TABLE、INSERT、SELECT、WHERE、LIKE、GROUP BY、SUM、COUNT、AVG、IS NOT NULL）

`*.sql` 是 SQL 檔（不是 Python），`sql.txt`、`null.txt` 是對答，`verify.md`、`decision.md` 是自評的表單，都不在檢查範圍。
`conftest.py` 是課程準備的空檔（讓 pytest 找得到同一個資料夾的 db_report.py），`ledger_db.py`、`run_sql.py` 是課程準備的小工具，不用改。
`entries.csv` 是課程編的假資料。`probe/` 是 check 用的小程式（學員不用看）。
