# 1-23 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-23 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（1-5 教過：f-string；這課用 rstrip、split）
- input
- 函式呼叫（int、repr）
- 比較與邏輯（含 assert、not、in）
- if
- for
- list
- tuple（1-14 教過：一筆帳是 tuple、for d, item, amount in entries 拆包）
- 函式定義（1-18 教過：def、參數、return、docstring）
- 模組與 import（1-21 教過：from pathlib import Path、from store import …）
- 檔案讀寫（這課教：with open(…, "w"／"a", encoding="utf-8") as f、f.write、for line in f、Path(__file__).parent / "ledger.txt"）
- class（例外：只有 Path(__file__).parent 的 .parent 這一處，整段當成「這個檔所在的資料夾」的固定寫法用；物件的屬性 1-24 才教）

`predict.txt`、`close.txt`、`tutor.md` 是文字檔，不是程式，不在檢查範圍。
`store.py` 是課程版本（凍結版）：學員不改它，第③圈用來回測試檢查它。
