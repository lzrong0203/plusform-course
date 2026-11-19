# 2-3 用到的概念

這課的示範、起點檔、正確版（`reference/`）、壞版本、參考答案，只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 2-3 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- 變數
- 資料型別
- 數字運算（`//`、`%`：1-4 的分帳零頭）
- 字串操作（`split("/")`、`startswith`、f-string）
- 函式呼叫（`int(...)`、`date.today()`、`strftime(...)`）
- 比較與邏輯（assert：1-8）
- if
- for（`range(people)`）
- list
- tuple 與 set（`("11/03", "午餐", "餐飲", 120)` 一筆帳；for 一次拆出四個欄位）
- 推導式與 zip（壞版本 m4 的 list 推導式）
- 函式定義（`def test_…():`；`@pytest.mark.parametrize(...)` 掛在 def 上面的 @ 那一行，1-24 的 @dataclass 是同一種寫法）
- 型別提示與 lambda（`lambda: date(2026, 11, 3)`：1-20 教過 lambda）
- 模組與 import（`import pytest`、`from split import split`、`from datetime import date`）
- 例外處理（`raise ValueError(...)`）
- 檔案讀寫（`with pytest.raises(ValueError):` 的 with：1-23 用 with 打開檔案，同一種寫法）
- class（`date(2026, 11, 3)` 做出一個日期、`today().strftime("%m/%d")` 呼叫它的方法：1-24 教過物件與方法）

`edges.md`、`decision.md` 是自評的表單，`review.txt` 是對答，都不是程式，不在檢查範圍。
`conftest.py` 是課程準備的空檔（讓 pytest 找得到同一個資料夾的 split.py），不用改。
這課第一次用 pytest（`uv add --dev pytest` 裝的）：測試函式名字用 test_ 開頭、`monkeypatch` 參數、`pytest.raises`、`@pytest.mark.parametrize`，都在 README 第 1 節講。
