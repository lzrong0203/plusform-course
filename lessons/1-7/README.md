# 1-7　讀懂錯誤訊息：Traceback 從最下面看

這課大約 45 分鐘。三圈比例 70／20／10。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）；VS Code 跳到第幾行的 Control G，Windows 一樣是 Ctrl＋G。
要會的：`print`、變數、資料型別（1-3 的 `type()`）、`//` 和 `%`（1-4）、字串的 `split()`、索引、f-string（1-5）、`int()`、`input()`（1-6）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 八支各藏一個錯的小程式（`p1.py`～`p8.py`）：每支第 1 行的註解寫著它要做什麼。**先猜**：只用眼睛看，它會出哪一種錯、在第幾行（可以寫在檔案最上面的註解裡）；**再跑**：`uv run lessons/1-7/p1.py`，照錯誤訊息從最下面看；**再修**：改好、存檔、再跑一次，印出註解寫的東西。影片裡八支都跑過一次，可以跟著做；修法要自己寫。

B. 錯誤配對（`match.txt`，對答 6 題）：6 行錯誤訊息的最後一行，各配一個原因（A～F）。

**第②圈：對照兩種求救。**

A. `ai_help.txt`（對答 3 題）：影片裡熊問同一個錯，一次只說「不能跑」，一次貼上四樣東西，判斷家教的兩個回答。完整的對話在 `補充.md`。

B. `my_help.md`（自評）：拿你自己看到的錯誤訊息，照四樣東西問家教：出事的程式、完整的錯誤訊息、我猜的原因、我試過什麼。

**第③圈：計時題（關掉 AI）。** 一支 20 行的程式 `shop.py`（課程準備的版本：週末採買，算總金額和每人付多少），跑起來會當掉。只靠錯誤訊息找出錯在哪裡，修好，讓它印出：

```
總金額 370 元
每人 123 元，零頭 1 元
```

**準備好了再開始**：到課程資料夾打 `uv run check.py timer 1-7`，它才把 `shop.py` 複製到你的帳本、開始計時。計時算到你最後一次存檔 `shop.py`；check 全對時會告訴你大約花了幾分鐘（參考：10 分鐘內）。**只記錄、不扣分**，也不擋你往下走；剛剛如果有用 AI，這個時間就不準。

## 2. 提示

- 錯誤訊息**從最下面看**：
  1. 最後一行：冒號前面是錯誤的種類（`NameError`、`TypeError`……），後面是原因。
  2. 往上一行：`^` 和 `~` 指出這一行的哪一段出事。
  3. 再往上：出事的那一行程式。
  4. 再往上：`File "…/p4.py", line 6`：哪個檔案、第幾行。
  5. 最上面：`Traceback (most recent call last):`，「最近發生的放在最後面」，所以從最下面看。
- `SyntaxError`、`IndentationError` 是 Python 看不懂寫法：**一行都不跑**，錯誤訊息也沒有 `Traceback` 那一行。其他四種（`NameError`、`TypeError`、`ValueError`、`ZeroDivisionError`）是跑到那一行才當掉：**前面的行已經跑了**，印出來的字會在錯誤訊息上面。
- 六種錯誤，白話：

| 最後一行 | 白話 | 常見的原因 |
|---|---|---|
| `SyntaxError` | 寫法 Python 看不懂 | 括號、引號沒有成對；括號打成全形 `（ ）` |
| `IndentationError` | 一行最前面的空白不對 | 這一行最前面多了空白（unexpected indent） |
| `NameError` | 這個名字還沒有 | 打錯字；還沒設定就先用。`Did you mean` 是 Python 猜的，不一定對 |
| `TypeError` | 種類不能這樣用 | 字串和數字用 `+` 接在一起 |
| `ValueError` | 種類對、內容不對 | `int("120元")`、`int("12.5")` |
| `ZeroDivisionError` | 除以 0 | 除號右邊的變數是 0 |

- **錯誤出現的地方，不一定是要改的地方。** 錯誤訊息引號裡的值（像 `'午餐'`）是程式實際拿到的東西；值不對，就往上找它是哪一行設的。
- 在 VS Code 跳到第幾行：先點一下上面的程式，按 `Control G`（Windows 是 `Ctrl G`），打行號、按 Enter。
- 求救的四樣：出事的程式、完整的錯誤訊息、我猜的原因、我試過什麼。家教說的話，要能對到錯誤訊息的哪一段，自己跑過再相信。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-7
```

它會把起點檔複製到你的帳本 `lessons/1-7/`：`p1.py`～`p8.py`、`match.txt`、`ai_help.txt`、`my_help.md`。計時題的 `shop.py` 不在這裡，要等你準備好了再打：

```bash
uv run check.py timer 1-7
```

用 VS Code 打開帳本，在 VS Code 下面的終端機（帳本資料夾）跑：

```bash
uv run lessons/1-7/p1.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-7
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-7`。課號寫 `1-07` 也可以。）

## 4. 成品示範

p4.py 修好以前：

```
$ uv run lessons/1-7/p4.py
午餐 120 晚餐 150
Traceback (most recent call last):
  File "/Users/bear/code/ledger/lessons/1-7/p4.py", line 6, in <module>
    print("一共", totl, "元")
                  ^^^^
NameError: name 'totl' is not defined. Did you mean: 'total'?
```

修好以後：

```
$ uv run lessons/1-7/p4.py
午餐 120 晚餐 150
一共 270 元
```

## 5. 怎麼測

`uv run check.py 1-7` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。一共 18 題：

- 第一圈：p1～p8 各 1 題（check 自己跑每一支，印出來要跟註解寫的一樣）、`match.txt` 6 題
- 第二圈：`ai_help.txt` 3 題
- 第三圈：計時題 `shop.py` 1 題（要先打 `uv run check.py timer 1-7`）

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。`my_help.md` 是自評，check 不檢查。

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-7 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡兩段家教對話的逐字紀錄、八支程式的錯誤訊息原文、Python 官方文件的原文、影片第③圈的 trip.py）在 `補充.md`。
