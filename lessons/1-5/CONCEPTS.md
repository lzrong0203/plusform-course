# 1-5 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，壞版本用到沒列的概念就不能收進題庫。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（索引、切片、strip、split、replace、startswith、f-string，這課教）
- 函式呼叫（例外：int() 把金額文字變成整數，1-3 第③圈用過；呼叫函式、拿回傳值到 1-6 才細講）
- list（例外：split() 交回的是一串文字，這課只用 parts[0]、parts[-1] 拿出第幾段，跟字串的索引一樣；list 到 1-13 才細講）
- 函式外殼（例外：split_item() 是課程版本包成的拆帳機，學員只寫案例表、不讀也不寫它；def 到 1-18 才教）
- tuple（例外：split_item() 用 return 交回品項和金額；學員在案例表只寫「兩個值用逗號隔開」，tuple 到 1-14 才教）

`guess.txt`、`ai_quiz.txt`、`my_quiz.md`、`cases.txt` 是文字檔，不是程式，不在檢查範圍。
