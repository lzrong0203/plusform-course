# 1-26 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-26 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（1-5 教過：f-string、strip、split、join、startswith）
- input
- 函式呼叫
- 比較與邏輯（含 assert、is None、not、in）
- if
- while
- for（含 enumerate 的 start=1）
- list
- dict
- 推導式（1-17 教過：total 裡的 sum(e.amount for e in entries)）
- 函式定義（1-18 教過：def、參數、return、docstring）
- 預設值與關鍵字參數（1-19 教過：confirm=False、start=1）
- 型別提示（1-20 教過：@dataclass 的欄位 date: str）
- 模組與 import（1-21 教過；logging、re 是標準函式庫的模組，這課只要看得懂 logging.warning、logging.info、re.compile、fullmatch、group 在做什麼）
- 例外處理（1-22 教過：try／except ValueError、raise ValueError）
- 檔案讀寫（1-23 教過：with open、encoding="utf-8"、Path(__file__).parent）
- class（1-24 教過：@dataclass 的 Entry；這課多看一種 @：@command 是自己寫的 decorator，等於 show = command(show)，學員只讀不寫）
- 課程沒教的寫法（例外：old_ledger.py 的 read_entries 用 yield（generator），這課只要看得懂「一次交出一筆、停在那裡，要下一筆時接着跑」，學員只讀不寫）

`read.txt`、`tutor.md` 是文字檔，不是程式，不在檢查範圍。
`old_ledger.py`（起點檔）是「熊的舊記帳程式」：寫法跟這門課不太一樣（自己寫的 @command、yield、logging、re），學員只加 delete 指令，其他的讀懂就好。
`delete_ai.py`（起點檔）是 AI 交回的固定版本（跟壞版本 1 一樣，差一）：學員不改它，第③圈用 assert 驗收。
`tests/probe_delete.py` 是 check 用的小程式（課程準備、學員看不到），用 contextlib 把載入時印的收起來，不在檢查範圍。
