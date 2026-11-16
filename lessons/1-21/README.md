# 1-21　模組與 import：別人寫好的工具，和 AI 編出來的套件

這課大約 50 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）；路徑的斜線兩邊寫法不同，用 `pathlib` 的 `Path` 接就不用管（第 2 節）。
要會的：def、參數、return（1-18）、f-string 的 `{amount:,}` 千分位（1-5）、assert（1-8）、`sum`（1-13）。前面好幾課作業裡「照抄就好」的那一行 `from 什麼 import 什麼`，這一課講清楚。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 把金額工具搬到 `money.py`。`main.py` 裡有兩個金額工具 `total`（把一串金額加起來）和 `fmt`（金額加上千分位和「元」）。把它們剪下、貼到旁邊的 `money.py`，`main.py` 改成一行 `from money import fmt, total`。兩個檔要放在同一個資料夾（帳本的 `lessons/1-21/`）。

B. `money.py` 最下面有三行它自己的檢查（兩條 assert、一行 print）。它們只該在「直接跑 money.py」的時候跑，被 `main.py` import 的時候不要跑：放進 `if __name__ == "__main__":` 下面（三行前面各空四格）。

C. `main.py` 用標準函式庫的 `datetime`：把兩個 `"…"` 換成格式碼，印出本月（今天的年和月，例如 `2026-11`），再用 `datetime.strptime` 把 `"2026-11-03"` 解析成日期，印出 `11 3`。

**第②圈：問家教格式碼，再對照官方文件。** 照 `tutor.md` 的步驟，在家教專案裡問 `%Y-%m-%d` 是什麼意思、寫成大寫 `%M` 會怎樣、官方文件哪裡查得到；再打開官方文件的格式碼表自己對照，記在 `tutor.md`（三個標籤都寫了就算交了，內容不改對錯）。再做查官方文件 3 題（`docs.txt`，每題附網址）。

**第③圈：AI 叫你 import 的，先查它存不存在（`imports.txt`，3 題）。** 標準函式庫的模組都列在 https://docs.python.org/3.13/py-modindex.html ；要另外裝的套件，到 https://pypi.org 搜尋名字。兩邊都查不到，就是編出來的名字：**不要裝**，也不要找名字很像的來裝，退回去請 AI 改用標準函式庫或你自己寫的檔。（怎麼判斷一個查得到的套件能不能裝，4-8 會再講。）

## 2. 提示

- **模組：** 一個 `.py` 檔就是一個模組，檔名去掉 `.py` 就是模組的名字（`money.py` → `money`）。`from money import fmt, total` 是「從 money 這個模組拿 fmt 和 total 來用」；`import math` 是整個模組拿進來，用的時候寫 `math.ceil(…)`。
- **import 會先把那個檔從頭跑一遍。** 所以 `money.py` 最外層的 print、assert，在 `main.py` import 它的時候都會跑。官方教學（6.1.1）：直接跑一個檔時，它的 `__name__` 是 `"__main__"`；被 import 的時候，`__name__` 是模組的名字（`"money"`），`if __name__ == "__main__":` 下面那段就不跑。你帳本的 `main.py`（0-C）最下面就有這兩行。
- **找得到 money.py 的條件：** 官方教學 6.1.2：import 先找「你跑的那個檔所在的資料夾」。`money.py` 不在 `main.py` 旁邊，就會出現 `ModuleNotFoundError: No module named 'money'`。
- **標準函式庫：** Python 自己帶的模組，裝好 Python 就有、不用另外裝。`datetime`（日期）、`random`（亂數）、`math`（數學）、`pathlib`（路徑）都是。
- **datetime 的格式碼：** `date.today()` 是今天；`.strftime("%Y-%m")` 照格式把日期變成字串；`datetime.strptime("2026-11-03", "%Y-%m-%d")` 反過來，把字串照格式解析成日期。`%Y` 四位數的年、小寫 `%m` 兩位數的月、`%d` 兩位數的日；**大寫 `%M` 是分鐘**，寫錯了不一定會出現錯誤訊息（`strptime("2026-11-03", "%Y-%M-%d")` 照樣跑，月份卻變成 1）。完整的表：https://docs.python.org/3.13/library/datetime.html#format-codes
- **random、math：** `random.randint(1, 6)` 每次跑都不一樣，可能是 1 到 6（官方文件：a <= N <= b，兩頭都包含）。`math.ceil(1250 / 3)` 是無條件進位，417。
- **pathlib（Mac／Windows 路徑不同）：** Mac 的路徑用斜線 `/`，Windows 用反斜線 `\`。`Path("lessons") / "1-21" / "money.py"` 在 Mac 印出 `lessons/1-21/money.py`，在 Windows 印出 `lessons\1-21\money.py`：用 `Path` 接，兩邊都對。
- **ModuleNotFoundError：** import 找不到那個模組。原因有兩種：這台電腦沒裝，或根本不存在。`uv run python -c "import 名字"` 可以只試 import、不裝任何東西；要分清楚是哪一種，到 PyPI 搜尋。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-21
```

它會把起點檔複製到你的帳本 `lessons/1-21/`：`money.py`、`main.py`、`docs.txt`、`tutor.md`、`imports.txt`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-21/money.py
uv run lessons/1-21/main.py
uv run python -c "import twmoney"
```

（最後一行只是試 import，不會裝任何東西；影片裡的 twmoney 是課程準備的、AI 編出來的那種名字，PyPI 查不到，不要去裝。）

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-21
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-21`。）

## 4. 成品示範

```
$ uv run lessons/1-21/money.py
money.py 自己的檢查都過了
$ uv run lessons/1-21/main.py
合計 1,820 元
本月 2026-11
11 3
```

`本月` 那一行是你跑的那一天的年和月。`main.py` 不會印出「money.py 自己的檢查都過了」。

## 5. 怎麼測

`uv run check.py 1-21` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。第一圈：直接呼叫 `money.py` 的 `total`、`fmt` 各兩次；直接跑 `money.py` 要印出自己的檢查；跑 `main.py` 要從 money 拿函式（`main.py` 裡不能再留一份 def）、印出合計、本月（照你跑的那一天算）、`11 3`，而且不能印出 money.py 自己的檢查；再把 `amounts` 換成別的金額跑一次。第二圈：`docs.txt` 3 題、`tutor.md` 三個標籤寫了沒；第三圈：`imports.txt` 3 題。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `ModuleNotFoundError: No module named 'money'` | `money.py` 不在 `main.py` 旁邊，或檔名打錯 | 兩個檔都放在帳本的 `lessons/1-21/`，檔名是 `money.py` |
| `NameError: name 'total' is not defined`（跑 money.py） | 函式還沒搬過來，最下面的檢查先用到了 | 把 `total`、`fmt` 貼到 money.py |
| 跑 main.py 也印出「money.py 自己的檢查都過了」 | 那三行還在最外層，import 時跟著跑 | 放進 `if __name__ == "__main__":` 下面 |
| `IndentationError` | `if` 下面那三行沒有空四格，或空格不一樣多 | 三行前面各空四格 |
| 「main.py 要用 from money import fmt, total」 | main.py 裡還留著 def total、def fmt | 剪下（不是複製）搬到 money.py |
| `ValueError: time data '2026-11-03' does not match format '…'` | 格式碼還沒換，或跟字串對不上 | `"%Y-%m-%d"`：中間的減號也要跟字串一樣 |
| 印出 `1 3`，不是 `11 3` | 月份寫成大寫 `%M`（分鐘） | 月份是小寫 `%m`，查官方文件的格式碼表 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-21 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、Python 官方文件的原文、AI 編出套件名稱的研究、PyPI 查詢的紀錄）在 `補充.md`。
