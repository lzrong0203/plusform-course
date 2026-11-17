# 1-C4 用到的概念

檢核站 4 只考 1-18～1-23 教過的東西（也會用到 1-1～1-17 的 print、變數、運算、if、for、list）。卷 A、卷 B（`B/`）、正確版、矯正包練習（`practice/`）都只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查。

## 可以用的概念

- 註解（1-1）
- print（1-1）
- 變數（1-2）
- 資料型別（1-3）
- 數字運算（1-4：//）
- 字串操作（1-5：f-string；1-23：rstrip、split）
- 函式呼叫（1-6：int()、repr()、len()）
- 比較與邏輯（1-8）
- if（1-9）
- for（1-11）
- list（1-13：append）
- tuple 與 set（1-14：拆包 d, item, amount = …）
- dict（1-15：矯正包練習 p_readfile.py 用 dict 放三個練習檔的內容）
- 函式定義（1-18：def、參數、return、docstring；沒有 return 交回 None；list 交進函式，函式裡改盒子裡面，外面看得到）
- 預設值與關鍵字參數（1-19：預設值、關鍵字參數；預設值 [] 只做一次；區域變數和全域變數）
- 型別提示與 lambda（1-20：參數後面的 : 型別、-> 型別，Python 跑的時候不檢查）
- 模組與 import（1-21：from pathlib import Path；import 會把那個檔從頭跑一遍；if __name__ == "__main__":）
- 例外處理（1-22：try、except ValueError、except ValueError as e、raise ValueError(訊息)；光禿禿的 except: 只出現在要學員找問題的 except.txt 和矯正包練習 p_swallow.py、p_broad.py、p_raise.py 的起點）
- 檔案讀寫（1-23：with open(…, encoding="utf-8") as f、for line in f、f.write、Path(__file__).parent / "檔名"）
- class（例外：只有 Path(__file__).parent 的 .parent 這一處，跟 1-23 一樣當成「這個檔所在的資料夾」的固定寫法用；物件的屬性 1-24 才教）

`trace.txt`、`except.txt` 是文字檔，裡面的程式不跑，不在 ast 檢查範圍；它們的程式也只用上面這些概念。
`sample.txt` 是第三部分給學員自己試的帳本檔（三筆），不是程式。
