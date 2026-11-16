# 1-19　函式（下）：預設值、關鍵字參數、範圍

這課大約 60 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：def、參數、return、呼叫時的小框、docstring（1-18）、名牌和盒子、`is`（1-16）、dict 的 `get`（1-15）、tuple 拆包（1-14）、預算燈號（1-9）、assert（1-8）、None（1-3）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 範圍題（`scope.txt`）：5 題，先不要跑，用眼睛追。

B. 修好預設值的陷阱（`add_entry.py`）。`add_entry(amount, book=[])` 沒給帳本時應該開一本新的，可是兩次呼叫共用了同一個 list。照官方教學的寫法改：預設值改成 `None`，函式裡 `book` 是 `None` 的時候才做一個新的空 list。最下面三行不要改，改好要印出 `[120] [65]`。

C. 把長程式拆成小函式（`split.py`）。`report_long.py` 是熊的月報表，同樣的步驟為了兩種預算（1000、1200）寫了兩次，一共六十多行。`split.py` 已經寫好五個函式的名字和說明：`total`、`by_category`、`biggest`、`light(s, budget=1000)`、`report(entries, budget=1000)`。把 `report_long.py` 對應的幾行搬進去：前四個用 `return` 交回結果，`report` 用前四個函式把報表印出來。最下面三行不要改，跑出來要跟 `report_long.py` 一模一樣。

**第②圈：請家教解釋你踩到的範圍錯誤，再出一題考它（`tutor.md`）。** 在家教專案裡貼上踩到的錯（`tutor.md` 有一段範例）和錯誤訊息的最後一行，請它用問題帶你想、先不要給改好的程式。想通以後，換你出一題同類型的（函式裡外有同一個名字）考它，請它直接回答；它答得對不對，自己跑一次確定。記在 `tutor.md`（六個標籤都寫了就算交了，內容不改對錯）。

**第③圈：需求寫進 docstring，函式內容交給 AI，用測試驗收。** 跟 1-18 一樣先寫三樣東西：

1. 函式的名字（`over_limit.py` 已經寫好 `def over_limit(amounts, limit=300):`）
2. docstring：寫清楚**輸入**（limit 沒給就是 300）、**輸出**、**例子**（例子寫一次真的呼叫和它交回的值）
3. assert：在 `checks_over_limit.py` 至少寫 3 條

把 def 那一行、docstring 和 assert 一起貼給 AI（免費的聊天版就可以），請它照 docstring 寫函式內容、assert 不要改，再把它寫的函式內容貼進 `over_limit.py`。**沒有 AI 帳號的**，打開課程資料夾的 `lessons/1-19/frozen/over_limit.py`（課程的凍結版，影片裡 AI 寫的那一份），把 docstring 下面的函式內容抄過來。課程另外藏了 3 個 AI 寫錯的版本（範例示意），你的 assert 要每一個都抓到；其中一個**第一次呼叫是對的、第二次才錯**。

## 2. 提示

- **預設值：** `def warn(total, budget=1000):` 的 `budget=1000`，意思是呼叫時沒給 budget 就用 1000。有預設值的參數要寫在沒有預設值的後面（`def warn(budget=1000, total):` 是 SyntaxError）。
- **關鍵字參數：** 呼叫時寫 `warn(1200, budget=1500)`，照名字交給 budget。寫了名字，順序就不重要（`warn(budget=1500, total=1200)` 一樣）；關鍵字要放在後面。1-1 的 `print(..., sep="/")`、`end=""` 就是關鍵字參數。
- **範圍：** 呼叫的時候開一個小框（1-18）。函式裡**給了值**的名字（`s = …`）是小框自己的，叫**區域變數**，函式跑完就不見；寫在函式外面的叫**全域變數**。函式裡只讀、沒給值的名字，框裡找不到就到外面找（官方教學：variable references first look in the local symbol table, … then in the global symbol table, and finally in the table of built-in names）。
- **UnboundLocalError：** 函式裡只要有一行給 `count` 值，整個函式裡的 `count` 都是框裡的；在給值之前先讀它（`count = count + 1` 的右邊、或前面先 `print(count)`），就會出現 `UnboundLocalError: cannot access local variable 'count' where it is not associated with a value`。看到它，先找函式裡有沒有給同一個名字值。
- **要改外面的數字：** 用參數交進去、用 `return` 交回來（`count = add_one(count)`），不要在函式裡偷改外面的。
- **預設值只做一次：** 預設值是 Python 讀到 def 那一行時就做好的（官方教學：The default value is evaluated only once）。預設值寫 `[]` 或 `{}`，每次呼叫都共用同一個盒子；改成 `None`，函式裡 `if book is None: book = []`。
- 第③圈的 assert：同一個檔案裡的 assert 照順序呼叫。只呼叫一次的檢查，抓不到「第一次對、第二次就錯」的版本。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-19
```

它會把起點檔複製到你的帳本 `lessons/1-19/`：`scope.txt`、`add_entry.py`、`report_long.py`、`split.py`、`tutor.md`、`over_limit.py`、`checks_over_limit.py`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-19/add_entry.py
uv run lessons/1-19/report_long.py
uv run lessons/1-19/split.py
uv run lessons/1-19/checks_over_limit.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-19
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-19`。）

## 4. 成品示範

```
$ uv run lessons/1-19/add_entry.py
[120] [65]
$ uv run lessons/1-19/split.py
== 11 月報表（預算 1000 元）==
合計 1045 元
  餐 505 元
  車 90 元
  書 450 元
最大的一筆 書 450 元
紅燈
== 11 月報表（預算 1200 元）==
合計 1045 元
  餐 505 元
  車 90 元
  書 450 元
最大的一筆 書 450 元
黃燈
$ uv run lessons/1-19/checks_over_limit.py
$
```

`checks_over_limit.py` 什麼都沒印出來，代表每一條 assert 都成立。

## 5. 怎麼測

`uv run check.py 1-19` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。第一圈：`scope.txt` 5 題、`add_entry.py`（有沒有 return、照順序呼叫三次（沒給帳本兩次、給了帳本一次）、整支跑一次）、`split.py`（直接呼叫 total、by_category、biggest、light 兩次、整支跑出來跟 report_long.py 一樣）；第二圈：`tutor.md` 六個標籤寫了沒；第三圈：`over_limit.py` 的 docstring 和 return、照順序呼叫 over_limit 四次、你的 assert 抓不抓得到 3 個 AI 寫錯的版本、你的 assert 在你的 over_limit.py 上全部成立。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `add_entry.py` 印出 `[120, 65] [120, 65]` | 預設值還是 `[]`，兩次呼叫共用同一個 list | 改成 `book=None`，函式裡 `if book is None: book = []` |
| 「add_entry(85, [120]) 應該回傳 [120, 85]」 | 有交帳本進來，你還是做了新的 | 只有 `book is None` 的時候才做新的 |
| `UnboundLocalError: cannot access local variable …` | 函式裡給了那個名字值，又在給值之前先讀它 | 用參數交進去、用 return 交回來 |
| `NameError: name 't' is not defined`（在函式外面） | t 是函式小框裡的名字，函式跑完就不見了 | 拿函式交回來的值（`x = make()`） |
| 「light(1045, budget=1200) 應該回傳 '黃燈'」 | 函式裡寫死了 1000 | `ratio = s / budget` |
| `split.py` 什麼都沒印 | report 還只有說明、沒有內容 | 把要印的幾行搬進 report |
| 「over_limit(…, limit=100) 應該回傳 [120, 450]」，交回的比較長 | 結果存在函式外面的 list，第二次接着加 | `result = []` 寫在函式裡面 |
| 第三圈「壞版本 1 沒抓到」 | 你的檔案裡只呼叫了一次 over_limit | 再寫一條 assert，呼叫第二次 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-19 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教、聊天版 AI 的完整對話、Python 官方文件的原文、global 為什麼這門課不用、函式小框裡的名字）在 `補充.md`。
