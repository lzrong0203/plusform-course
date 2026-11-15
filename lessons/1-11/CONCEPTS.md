# 1-11 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，壞版本用到沒列的概念就不能收進題庫，免得變成刁難題；
比 1-11 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print（含 end，1-1 教過）
- 變數
- 資料型別
- 數字運算
- input
- 函式呼叫
- 比較與邏輯
- if
- while
- for（for、range、enumerate：這一課教）
- list（例外：方括號只當成「一串數字」，用 for 一個一個拿出來，不教索引、append、修改；1-13 再細講）
