# 1-3 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，壞版本用到沒列的概念就不能收進題庫。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別（int、float、str、bool、None，這課教）
- 函式呼叫（例外：起點檔 entry.py 的 type() 照抄就好；正確版和壞版本裡的 int()、float() 學員不用看懂；呼叫函式到 1-6 才細講）
- 函式外殼（例外：to_yuan() 是課程版本包成的轉換機，學員只寫案例表、不讀也不寫它；def 到 1-18 才教）
- 字串操作（例外：正確版和壞版本裡的 replace、strip、isdigit，學員不用看懂；1-5 才教）
- if（例外：只有壞版本 1、2 用到，學員不用看懂；1-9 才教）

`types.txt`、`cases.txt`、`my_words.md` 是文字檔，不是程式，不在檢查範圍。
