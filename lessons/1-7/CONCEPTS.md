# 1-7 用到的概念

這課的示範、起點檔、正確版（`reference/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（split、f-string，1-5 教過）
- 函式呼叫（int()，1-6 教過）
- list（例外：p8.py 用 split() 交回的一串文字，只用 parts[2] 拿出第幾段，跟 1-5 的 parts[0]、parts[-1] 一樣；list 到 1-13 才細講）

起點的 p1～p8 每支都故意藏了一個錯（p1、p2、p3 是 Python 看不懂的寫法，不做概念檢查）。
`match.txt`、`ai_help.txt`、`my_help.md` 是文字檔，不是程式，不在檢查範圍。計時題的 `start_timed/shop.py` 由 `uv run check.py timer 1-7` 複製。
