# 1-C3 用到的概念

檢核站 3 只考 1-13～1-17 教過的東西（也會用到 1-1～1-11 的 print、變數、運算、if、for）。卷 A、卷 B（`B/`）、正確版、矯正包練習（`practice/`）都只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查。

## 可以用的概念

- 註解（1-1）
- print（1-1）
- 變數（1-2）
- 資料型別（1-3）
- 數字運算（1-4）
- 函式呼叫（1-6：len()、sum()、sorted()、enumerate()、zip() 這種呼叫別人寫好的函式）
- 比較與邏輯（1-8：>、<、>=、<=、==、!=、and、or、not、in）
- if（1-9）
- for（1-11：for、range、enumerate 的 start）
- list（1-13：索引、切片、append、insert、remove、pop、len、in、sum、sort()、sorted()；1-16：b = a 是同一個 list、copy() 做出另一個）
- tuple 與 set（1-14：tuple、for 後面拆包、set()、add、去掉重複）
- dict（1-15：鍵和值、d[鍵] = 值 新增或換掉、get(鍵, 預設值)、items()、len、for 拿到的是鍵、dict 記得放進去的順序）
- 推導式與 zip（1-17：[放進去的東西 for 名字 in 一串 if 條件]、zip 把兩串配成一對對）

`trace.txt` 是文字檔，裡面的程式不跑，不在 ast 檢查範圍；它的三段程式也只用上面這些概念。
第二部分的 `parsons.py` 起點檔是打亂、沒有縮排的程式行（Python 看不懂），不做概念檢查；正確版 `reference/parsons.py` 照樣檢查。
矯正包練習裡故意打亂縮排的 `p_indent.py` Python 看不懂，也不做概念檢查。
