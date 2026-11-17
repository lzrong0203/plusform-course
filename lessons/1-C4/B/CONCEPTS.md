# 1-C4 卷 B 用到的概念

檢核站 4 只考 1-18～1-23 教過的東西。卷 B 跟卷 A 一樣（每一題考的概念跟卷 A 同一題相同），正確版都只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查。

## 可以用的概念

- 註解（1-1）
- print（1-1）
- 變數（1-2）
- 資料型別（1-3）
- 數字運算（1-4）
- 字串操作（1-5：f-string；1-23：rstrip、split）
- 函式呼叫（1-6：int()）
- 比較與邏輯（1-8）
- if（1-9）
- for（1-11）
- list（1-13）
- tuple 與 set（1-14：拆包 d, way, amount = …）
- 函式定義（1-18：def、參數、return、docstring）
- 預設值與關鍵字參數（1-19）
- 型別提示與 lambda（1-20：型別提示）
- 模組與 import（1-21：from pathlib import Path、import tools、if __name__ == "__main__":）
- 例外處理（1-22：光禿禿的 except: 只出現在要學員找問題的 except.txt）
- 檔案讀寫（1-23：with open(…, encoding="utf-8") as f、for line in f、Path(__file__).parent / "檔名"）
- class（例外：只有 Path(__file__).parent 的 .parent 這一處，跟 1-23 一樣當成固定寫法用；1-24 才教）

`trace.txt`、`except.txt` 是文字檔，裡面的程式不跑，不在 ast 檢查範圍。`sample.txt` 是給學員自己試的付款紀錄檔（三筆），不是程式。
