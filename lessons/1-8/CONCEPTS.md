# 1-8 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，壞版本用到沒列的概念就不能收進題庫，免得變成刁難題；
比 1-8 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- input
- 函式呼叫（int()、input() 這種「呼叫別人寫好的函式」，1-6 教過；over_budget() 也是用呼叫的）
- 比較與邏輯（這課教：==、!=、>、<、>=、<=、and、or、not、真假值、assert）
- 函式外殼（例外：over_budget() 是課程版本包成的函式，學員只呼叫、不定義；def 到 1-18 才教）
- 模組與 import（例外：只有 from budget import over_budget 這一行，照抄就好；1-21 才教）

`truth.txt`、`ai_check.txt`、`my_test.md` 是文字檔，不是程式，不在檢查範圍。
