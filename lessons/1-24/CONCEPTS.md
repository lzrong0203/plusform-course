# 1-24 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-24 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（1-5 教過：f-string、startswith）
- 函式呼叫
- 比較與邏輯（含 assert、is None、not、in）
- if
- for
- list
- tuple
- 函式定義（1-18 教過：def、參數、return、docstring）
- 型別提示（1-20 教過：date: str 這種寫法，這課拿來寫 @dataclass 的欄位）
- 模組與 import（1-21 教過：from dataclasses import dataclass、from ledger_ai import …）
- class（這課教：class、__init__、self、屬性、方法、@dataclass；繼承看得懂就好：ledger_ai.py 的 class Ledger(BaseLedger)、super().add(…) 是 AI 交回的版本，學員只讀不寫）

`predict.txt`、`review.txt`、`tutor.md` 是文字檔，不是程式，不在檢查範圍。
`ledger_ai.py`（起點檔）是 AI 交回的固定版本：學員不改它，第③圈用 assert 驗收 biggest、再讀一遍判斷收不收。
`tests/probe_entry.py`、`tests/probe_ledger.py` 是 check 用的小程式（課程準備、學員看不到），用 contextlib 把學員檔案最下面的 print 收起來，不在檢查範圍。
