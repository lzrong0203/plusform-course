# 1-20 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-20 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別（含 type()：1-3 教過）
- 數字運算（含 //：1-4 教過）
- 字串操作（1-5 教過：索引、切片；這課的 e[0]、e[2]、[:3] 是同一種寫法，用在 tuple 和 list）
- 函式呼叫（len、sorted、any、all）
- 比較與邏輯（含 assert、not）
- if
- for
- list（1-13 教過：sorted、切片 [:3]、索引）
- tuple 與 set（1-14 教過：tuple、拆包 for date, cat, amount in …）
- dict（1-15 教過：get(鍵, 0)、items()）
- 推導式與 zip（1-17 教過：any／all 括號裡的寫法跟推導式一樣讀）
- 函式定義（1-18 教過：def、參數、return、docstring）
- 預設值與關鍵字參數（1-19 教過：reverse=True 是關鍵字參數）
- 型別提示與 lambda（這課教：參數後面的 `: 型別`、`-> 型別`（Python 跑的時候不檢查）；lambda；sorted 的 key、reverse、穩定排序；any、all；`*args`、`**kwargs`）
- 模組與 import（例外：只有 checks_top3.py 的 from top3 import top3 這一行，照抄就好；1-21 才教）

`predict.txt`、`translate.txt`、`tutor.md` 是文字檔，不是程式，不在檢查範圍。
`deep.py` 是選做加深（遞迴，check 不檢查）。
`frozen/top3.py` 是課程的凍結版（第③圈 AI 照 docstring 寫的版本，給沒有 AI 帳號的學員抄函式內容），不是起點檔。
