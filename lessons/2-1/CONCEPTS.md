# 2-1 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 2-1 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（1-5 教過 f-string；正確版裡的 `{amount:>5,}` 是 AI 交回來的寫法：`>5` 靠右佔五格、`,` 千分位逗號，這課讀得懂就好，不用自己寫）
- 函式呼叫
- for
- list
- tuple 與 set（for 一次拿出一筆 tuple 的四個欄位）
- dict（1-15 教過：totals.get(…, 0) 加總、.items()）

`expected.txt`、`commands.txt` 是文字檔，`decision.md`、`account.md` 是自評的表單，不是程式，不在檢查範圍。
這課第一次讓 AI（VS Code 裡 Copilot 的 agent）改帳本裡的檔案：`report.py` 最後的樣子是學員收下的那一份，check 只看它印出來的跟 expected.txt 一不一樣。
