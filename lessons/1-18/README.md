# 1-18　函式（上）：def、參數、return

這課大約 50 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：for 與累加（1-11）、list 的 `append`、`pop`（1-13）、tuple 拆包（1-14）、dict 的 `get`（1-15）、名牌和盒子（1-16）、assert（1-8）、None（1-3）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 先猜（`predict.txt`）：3 題，先不要跑，用眼睛追。

B. 把加總包成函式（`total.py`）。檔案裡同一段加總寫了兩次（11 月、12 月）。在最上面寫一個函式 `total(amounts)`，一筆一筆加起來，最後用 `return` 交回合計；再把下面兩段改成呼叫 `total`，一樣印出兩個月的合計。函式裡不要 `print`。

C. 把一筆加進帳本（`add.py`）。寫一個函式 `add_entry(book, amount)`，把 `amount` 加到 `book` 的最後面。最下面四行不要改。

**第②圈：請家教審你的函式名稱和拆法（`tutor.md`、`names_quiz.txt`）。** 在家教專案裡貼上你寫的函式（`tutor.md` 有一段範例），請它審：名字有沒有說清楚它在做什麼、每個函式是不是只做一件事；先不要幫你改寫。家教說要改的，先想清楚為什麼，不同意就說出理由、自己跑一次確定。記在 `tutor.md`（自評，不擋過關）。`names_quiz.txt` 有四題。

**第③圈：需求寫進 docstring，函式內容交給 AI，用測試驗收。** 從這課起，要交給 AI 寫的函式，你先寫三樣東西：

1. 函式的名字（`by_category.py` 已經寫好 `def by_category(entries):`）
2. docstring：在 def 下面用三個引號寫清楚**輸入**、**輸出**、**例子**（例子寫一次真的呼叫和它交回的值）
3. assert：在 `checks_by_category.py` 至少寫 3 條，其中一條交**空的 list** 進去

把 def 那一行、docstring 和 assert 一起貼給 AI（免費的聊天版就可以），請它照 docstring 寫函式內容、assert 不要改，再把它寫的函式內容貼進 `by_category.py`。**沒有 AI 帳號的**，打開課程資料夾的 `lessons/1-18/frozen/by_category.py`（課程的凍結版，影片裡 AI 寫的那一份），把 docstring 下面的函式內容抄過來。AI 寫的對不對，交給你的 assert 判斷：課程另外藏了 3 個 AI 寫錯的版本（範例示意），你的 assert 要每一個都抓到。`docstring.md` 是檢核表（自評）。

## 2. 提示

- **函式＝把一段程式包起來、取一個名字。** `def` 後面接名字和括號，括號裡是**參數**（呼叫的時候接住交進來的東西），最後一個冒號；下面縮排的幾行是函式的內容。`def` 這幾行只是把步驟記下來，叫到它的名字（呼叫）才會跑。
- **呼叫的時候，Python 開一個新的小框**（官方教學：The execution of a function introduces a new symbol table used for the local variables of the function）：參數和函式裡的變數都在這個小框裡，函式跑完小框就收起來，裡面的名字外面找不到。
- **return 把一個值交回呼叫的地方。** `print(total(nov))` 先算 `total(nov)`，交回 505，就像那一段換成了 505，再交給 print。
- **print 和 return 不一樣。** print 只是印在終端機給人看；呼叫的地方要拿到值，一定要 return。**沒有 return 的函式，交回的是 None**（官方教學：even functions without a return statement do return a value… This value is called None）。拿到 None 的時候，先看函式裡是不是只寫了 print。
- **list 交進函式，函式裡的名字和外面的名字指着同一個盒子。** 函式裡改盒子裡面（`append`、`pop`），外面看得到；函式裡寫 `book = …` 是把函式裡的名牌換到新的盒子，外面不變（1-16 的換盒子、改盒子）。官方教學的註腳：if a mutable object is passed, the caller will see any changes the callee makes to it。1-13 呼叫 `remove_last(a)` 以後 `a` 少一筆，就是這個原因。不想被改，交進去之前先 `copy()`。
- **docstring＝def 下面第一行、用三個引號寫的說明**（官方教學：this string literal is the function’s documentation string, or docstring），`help(函式名稱)` 會把它印出來。第一行一句話說它做什麼，第二行空一行，下面寫輸入、輸出、例子。
- 第③圈的 assert：同一類的要加起來、兩類各自加、空的 list 交回 `{}`。只檢查「有資料」的情況，空的 list 交回 `None` 的版本抓不到。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-18
```

它會把起點檔複製到你的帳本 `lessons/1-18/`：`predict.txt`、`total.py`、`add.py`、`names_quiz.txt`、`tutor.md`、`by_category.py`、`checks_by_category.py`、`docstring.md`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-18/total.py
uv run lessons/1-18/add.py
uv run lessons/1-18/checks_by_category.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-18
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-18`。）

## 4. 成品示範

```
$ uv run lessons/1-18/total.py
11 月合計 505 元
12 月合計 265 元
$ uv run lessons/1-18/add.py
[120, 85, 300, 45]
$ uv run lessons/1-18/checks_by_category.py
$
```

`checks_by_category.py` 什麼都沒印出來，代表每一條 assert 都成立。

## 5. 怎麼測

`uv run check.py 1-18` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。第一圈：`predict.txt` 3 題、`total.py`（有沒有 def 和 return、直接呼叫 total 三次（含空的 list）、整支跑兩次）、`add.py`（有沒有 def、跑兩次，第二次把 nov 換掉）；第二圈：`names_quiz.txt` 4 題；第三圈：`by_category.py` 的 docstring 和 return、直接呼叫 by_category 三次（含空的 list）、你的 assert 抓不抓得到 3 個 AI 寫錯的版本、你的 assert 在你的 by_category.py 上全部成立。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。`tutor.md`、`docstring.md` check 不檢查。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| 「回傳 None，常常是用了 print，而不是 return」 | 函式裡只 print、沒有 return | 函式最後寫 `return s`，print 移到呼叫的地方 |
| 「total 裡沒有 return」 | 同上（check 看程式的樣子就看得出來） | 同上 |
| `NameError: name 'total' is not defined` | 還沒寫 def，或呼叫寫在 def 前面 | def 寫在最上面，呼叫寫在下面 |
| `NameError: name 's' is not defined`（在函式外面） | s 是函式小框裡的名字，函式跑完就不見了 | 要用合計，拿函式交回來的值（`x = total(nov)`） |
| add.py 第二題沒過 | 函式裡寫死了 nov，或另外做了一個新的 list | 函式裡改交進來的 `book`：`book.append(amount)` |
| 「docstring：『例子』要寫一次真的呼叫」 | 例子只寫了文字，沒有呼叫 | 寫成 `by_category([("餐", 120), ("餐", 85)]) 是 {"餐": 205}` |
| 第三圈「壞版本 3 沒抓到」 | 沒有一條交空的 list 進去 | 加一條 `assert by_category([]) == {}` |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-18 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教、聊天版 AI 的完整對話、Python 官方文件的原文、函式小框裡的名字、函式裡換盒子和改盒子、`help()` 印出 docstring）在 `補充.md`。
