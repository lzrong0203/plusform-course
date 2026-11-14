# 1-6 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，壞版本用到沒列的概念就不能收進題庫。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（strip、replace、f-string，1-5 教過）
- input（這課教：先印提示、等你打字、交回字串）
- 函式呼叫（這課教：len()、int()、float()、input() 都是別人寫好的函式，括號裡放引數、拿回回傳值；回傳值可以直接放進另一個函式的括號）

`guess.txt`、`ai_ask.txt`、`my_ask.md`、`inputs.txt`、`expected.txt` 是文字檔，不是程式，不在檢查範圍。
