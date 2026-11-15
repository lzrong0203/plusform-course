# 1-17 用到的概念

這課的示範、起點檔、正確版（`reference/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-17 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 函式呼叫（len、sum）
- 比較與邏輯（含 assert）
- if
- for（含 enumerate：1-11 教過，這課複習 start）
- list（1-13 教過：空的 list、append、len、sum）
- tuple 與 set（1-14 教過拆包：for d, a in zip(…) 的 d, a）
- 推導式與 zip（這課教：[放進去的東西 for 名字 in 一串 if 條件]、zip 把兩串配成一對對、長度不同停在比較短的那一串）

`predict.txt`、`short_quiz.txt`、`describe_quiz.txt`、`tutor.md`、`describe.md` 是文字檔，不是程式，不在檢查範圍。
`answer.py` 是學員把 AI 寫的程式貼進來的檔：課程只放資料那兩行（起點檔）和一份正確版（reference，用這課學過的寫法），學員貼進來的寫法 check 不管，只跑測試。
