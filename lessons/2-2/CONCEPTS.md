# 2-2 用到的概念

這課的示範、起點檔、正確版（`reference/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 2-2 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（f-string：`{amount:,}` 千分位逗號、`{amount:>5,}` 靠右佔五格，2-1 讀過）
- 函式呼叫
- for
- list
- tuple 與 set（for 一次拿出一筆 tuple 的四個欄位）
- dict（totals.get(…, 0) 加總、.items()）
- 預設值與關鍵字參數（`justify="right"`、`title="11 月月報"`）
- 模組與 import（`from rich.table import Table`：從裝好的套件 import，1-21 教過 import 自己寫的模組與標準庫）
- class（`Table(...)` 做出一張表、`table.add_row(...)` 呼叫它的方法，1-24 教過）

`pypi.md`、`decision.md` 是自評的表單，`deps.txt` 是對答，都不是程式，不在檢查範圍。
這課第一次裝別人寫的套件（rich）；`report.py` 最後的樣子是學員收下的那一份（agent 改的），check 只看它在乾淨複本上跑不跑得起來、表格對不對齊。
