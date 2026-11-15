# 1-15 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查，壞版本用到沒列的概念就不能收進題庫，免得變成刁難題；
比 1-15 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算（含 round，1-4 起用過；剛好一半時選偶數的細節在補充.md）
- 字串（含 f-string，1-5 教過）
- input
- 函式呼叫
- 比較與邏輯（含 assert，1-8 教過）
- if
- while（含 break，1-10 教過）
- for（for、range、enumerate，1-11 教過）
- list（1-13 教過）
- tuple 與 set（1-14 教過：拆包、for 後面拆包）
- dict（這課教：大括號、鍵和值、d[鍵] 拿值、d[鍵] = 值 新增或換掉、len、in 問鍵、KeyError、get(鍵, 預設值)、items()、keys()、values()、sum(d.values())、for 拿到的是鍵、計數 d.get(k, 0) + 1、list 裡放 dict、dict 記得放進去的順序、兩個 dict 用 == 比）
- 函式外殼（例外：shares() 是課程版本包成的函式，學員只呼叫、不定義；def 到 1-18 才教）
- 模組與 import（例外：只有 from share import shares 這一行，照抄就好；1-21 才教）

`predict.txt`、`dict_quiz.txt`、`req_fix.txt`、`lead.md` 是文字檔，不是程式，不在檢查範圍。
