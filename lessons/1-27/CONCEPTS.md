# 1-27 用到的概念

這一關的考卷、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念（第 1 級 1-1～1-26 教過的）。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，用到沒列的概念就不能收進題庫；
比 1-27 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（1-5 教過：f-string、replace、strip、rstrip、split、startswith、isdigit）
- input
- 函式呼叫
- 比較與邏輯（含 assert、not、in）
- if
- while
- for（含 range、enumerate）
- list
- tuple 與 set（1-14 教過：拆包 s, n = …）
- dict（1-15 教過：get(鍵, 預設值)、items()、copy()）
- 推導式與 zip（1-17 教過：sum(x.amount for x in book)、zip）
- 函式定義（1-18 教過：def、參數、return、docstring）
- 預設值與關鍵字參數（1-19 教過：picked=[] 的陷阱、reverse=True）
- 型別提示與 lambda（1-20 教過：text: str -> int、sorted 的 key、lambda、any）
- 模組與 import（1-21 教過：from dataclasses import dataclass、from pathlib import Path、if __name__ == "__main__"）
- 例外處理（1-22 教過：try／except ValueError、raise ValueError）
- 檔案讀寫（1-23 教過：with open、encoding="utf-8"、"w"、Path(__file__).parent、exists()）
- class（1-24 教過：@dataclass 的 Entry）

`trace.txt`、`plain.txt`、`explain.md` 是文字檔，不是程式，不在檢查範圍。
`ledger_v1.py`（起點檔）最下面的 `main()` 是課程寫好的選單，學員不用改；五樣（Entry、to_yuan、load、save、totals）是學員手寫的。
`budget_ai.py`（start_later）是 AI 交回的固定版本（跟壞版本 2 一樣）：學員不改它，第三部分用 assert 驗收。
`tests/probe_*.py` 是 check 用的小程式（課程準備、學員看不到），用 contextlib 把載入時印的收起來，不在檢查範圍。
