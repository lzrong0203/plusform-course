# 1-16 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，壞版本用到沒列的概念就不能收進題庫，免得變成刁難題；
比 1-16 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（切片 [:]：1-5 學過，1-13 用在 list 上；這課用 a[:] 複製一份）
- 函式呼叫（這課多一個 id()：交回一個整數，代表這個物件是誰）
- 比較與邏輯（含 assert；這課教 is：問兩個名字是不是同一個物件）
- list（1-13 教過：索引、切片、append、len、sum；這課教 copy() 和 [:] 複製一份、b = a 不是複製）
- tuple 與 set（1-14 教過：tuple 不能改，這課拿來對照「不能改裡面」的型別）
- 模組與 import（例外：只有 from budget import fixed, nov, dec 這一行，照抄就好；1-21 才教）

`predict.txt`、`final_a.txt`、`tutor.md` 是文字檔，不是程式，不在檢查範圍。
