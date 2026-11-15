# 1-12 卷 B 用到的概念

這一關卷 B 的考卷、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念（1-1～1-11 教過的）。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，用到沒列的概念就不能收進題庫；
比 1-12 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（切片、f-string，1-5 教過）
- input
- 函式呼叫（int()、input() 這種「呼叫別人寫好的函式」，1-6 教過）
- 比較與邏輯（含 assert，1-8 教過）
- if（if、elif、else）
- while（while、break、continue）
- for（for、range、enumerate，1-11 教過）
- list（例外：方括號只當成「一串數字」，用 for 一個一個拿出來，跟 1-11 一樣；1-13 再細講）
