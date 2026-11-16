# 1-23　檔案讀寫：關掉程式，帳還在

這課大約 45 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）；路徑一律用 `Path` 接，Mac 和 Windows 寫法一樣。
要會的：tuple 拆包（1-14）、f-string（1-5）、for（1-11）、def 和 return（1-18）、`from pathlib import Path`、用斜線接路徑（1-21）、讀 Traceback（1-22）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 先猜（`predict.txt`）：3 題，先不要跑。w 和 a 差在哪、只寫檔名的時候檔案會跑到哪裡。

B. 把帳寫進檔案（`save.py`）。起點檔已經有三筆帳 `entries`。在下面用 `with open` 把每一筆寫成一行：

```python
with open(p, "w", encoding="utf-8") as f:
    for d, item, amount in entries:
        f.write(f"{d},{item},{amount}\n")
```

- `"w"`：寫入。檔案還沒有就新建一個；**已經有的話，一打開就先清空**，再寫。
- `encoding="utf-8"`：中文用 UTF-8 存。這課的每一個 open 都要寫（為什麼，看第 2 節）。
- `as f`：幫打開的檔案取名叫 f；下面空四格的，都是檔案開著的時候做的事。with 那一段做完，Python 自動關檔。
- 最後的 `\n` 是換行：每一筆一行。

C. 讀回來（`read.py`）。用 `with open(p, encoding="utf-8") as f:`（沒寫 `"w"` 就是讀），`for line in f:` 一次拿一行：

- 每一行最後有一個換行，`row = line.rstrip("\n")` 把它拿掉；
- `d, item, amount = row.split(",")` 用逗號切開；
- 讀回來的都是文字，金額要 `int(amount)` 才能加進 `total`；
- 每一筆印出 `11/03 午餐 120 元` 這樣的一行（`print(d, item, amount, "元")`），最後印合計。

D. 路徑跟著檔案走。兩個檔的第 6 行 `p = "ledger.txt"` 都改成：

```python
p = Path(__file__).parent / "ledger.txt"
```

只寫 `"ledger.txt"` 是相對路徑：Python 從「你在哪個資料夾打指令」去找。你在帳本資料夾打 `uv run lessons/1-23/save.py`，檔案就寫到帳本最上層；進到 `lessons/1-23` 再跑 read.py，就找不到它（FileNotFoundError）。`__file__` 是這個 .py 檔的路徑，`.parent` 是它所在的資料夾，再用斜線接上檔名：不管在哪裡跑，都是 save.py 旁邊的那個 ledger.txt。

**第②圈：請家教問你 with 的問題。** 照 `tutor.md` 的步驟：貼上你 save.py 裡 with 那幾行，請家教先不要給答案、問你一個問題；它要你試的，自己跑跑看，把結果貼回去，記在 `tutor.md`（四個標籤都寫了就算交了，內容不改對錯）。再做 `close.txt` 3 題。

**第③圈：來回測試（`checks_store.py`）。** 熊想在每筆帳加上備註，存檔、讀檔交給 `store.py`：

| 函式 | 說明（docstring） |
|---|---|
| `save_entries(path, entries)` | 把一串 (日期, 項目, 金額, 備註) 存進 path，整個檔案重寫 |
| `load_entries(path)` | 從 path 讀回一串 (日期, 項目, 金額, 備註)，金額是整數 |

需求只有一句：**存了再讀回來，要一模一樣**。起點檔給了一個小幫手 `roundtrip(entries)`（存進測試檔、再讀回來），每一條檢查都寫成：

```python
b = [("11/03", "午餐", 120, "跟同事"), ("11/04", "公車", 15, "")]
assert roundtrip(b) == b
```

`store.py` 是課程版本（凍結版，不要改它）。課程另外藏了 3 個 AI 照同一份說明寫錯的版本（範例示意）。你的檢查（至少 3 條）要在課程版本上全部成立、在每個寫錯的版本上至少有一條不成立。想想哪些帳最容易存壞：好幾筆、空的帳本 `[]`。

最後再寫一條：**備註裡有逗號**，例如 `"跟小明, 小華"`。跑跑看：

```bash
uv run lessons/1-23/checks_store.py
```

課程版本用逗號分隔欄位，備註裡的逗號會把一行切成五段，裝不進四個名字，跳出 `ValueError: too many values to unpack`。**這課先不修**，在那一行最後加上 `# 已知會當掉` 記下來（把它放在最後一條，前面的檢查才跑得到）。2-4 會用 csv 模組解決。

## 2. 提示

- **w 和 a：** `"w"` 一打開就先清空檔案（官方文件：truncating the file first），適合「整份重寫」；`"a"` 不清空，寫的字接在最後面（appending），適合「記一筆就加一行」。不確定的時候，跑完打開 ledger.txt 看一眼。
- **with 會自動關檔：** with 那一段做完（就算中間出錯），Python 會自動關檔。`f.write` 寫的字會先放在 Python 手上的暫存區，關檔時才一定寫進檔案；官方教學也寫：沒有 with、也沒有 `f.close()`，寫的字可能沒有完整寫進去。所以一律用 with 開。
- **為什麼一律寫 `encoding="utf-8"`：** 沒寫的時候，Python 3.13 用系統的地區設定（locale）編碼。Mac 通常是 UTF-8，所以在 Mac 上不容易出事；繁體中文的 Windows 常見是 cp950，用它讀 UTF-8 存的中文，會跳出 `UnicodeDecodeError` 或變成亂碼。Python 3.15 起預設改成 UTF-8，但官方還是建議一律寫上（各版本都一樣）。
- **讀回來的都是文字：** `"120"` 跟 `120` 不一樣，要加要比都先 `int(...)`。
- **相對路徑：** 只寫檔名，是從「現在在哪個資料夾執行」算起。`Path(__file__).parent / "ledger.txt"` 跟著 .py 檔走，Mac、Windows 都不用自己寫斜線或反斜線。
- **FileNotFoundError：** 找不到檔案。先想：是在哪個資料夾跑的？檔案真的在那裡嗎？

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-23
```

它會把起點檔複製到你的帳本 `lessons/1-23/`：`predict.txt`、`save.py`、`read.py`、`close.txt`、`tutor.md`、`store.py`（課程版本，不要改）、`checks_store.py`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看，再進到 `lessons/1-23` 跑一次 read.py，兩邊都要讀得到：

```bash
uv run lessons/1-23/save.py
uv run lessons/1-23/read.py
cd lessons/1-23
uv run read.py
cd ../..
uv run lessons/1-23/checks_store.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-23
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-23`。）

## 4. 成品示範

```
$ uv run lessons/1-23/save.py
存好了
$ uv run lessons/1-23/read.py
11/03 午餐 120 元
11/04 公車 15 元
11/05 晚餐 180 元
合計 315 元
```

`lessons/1-23/ledger.txt`（在 VS Code 左邊的檔案總管點開）：

```
11/03,午餐,120
11/04,公車,15
11/05,晚餐,180
```

## 5. 怎麼測

`uv run check.py 1-23` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。**check 會在系統的暫存資料夾裡擺一個假帳本，把你的檔複製過去再跑，不會動你帳本裡真的 ledger.txt。**

第一圈：`predict.txt` 3 題、`save.py`（從帳本資料夾跑，ledger.txt 要寫在 save.py 旁邊、三行一模一樣；每個 open 都要寫在 with 後面、寫 encoding="utf-8"）、`read.py`（先跑 save.py，再進 lessons/1-23 跑 read.py，印出三筆和合計 315 元）、來回測試（save.py 換成一筆 12/01 書 450 再存一次，從帳本資料夾跑 read.py，只印出新的那一筆）；第二圈：`close.txt` 3 題、`tutor.md` 四個標籤寫了沒；第三圈：你的來回測試抓不抓得到 3 個 AI 寫錯的版本、備註有逗號那一條有沒有標「# 已知會當掉」。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| 「ledger.txt 跑到帳本最上層去了」 | p 還是 `"ledger.txt"`（相對路徑） | 改成 `p = Path(__file__).parent / "ledger.txt"` |
| 「open(…) 裡要寫 encoding="utf-8"」 | 有一個 open 沒寫編碼 | 每個 open 都加 `encoding="utf-8"` |
| 「open(…) 要寫在 with 後面」 | 用了 `f = open(…)` | 改成 `with open(…) as f:`，下面空四格 |
| ledger.txt 只有一行、日期黏在一起 | 少了 `\n` | `f.write(f"{d},{item},{amount}\n")` |
| `FileNotFoundError: … 'ledger.txt'` | 在別的資料夾跑、找不到檔案 | 兩個檔的 p 都改成跟著檔案走 |
| `ValueError: not enough values to unpack` | 那一行切出來不到三段（例如空的一行） | 檢查 ledger.txt 有沒有多出空行；`f.write` 只在最後加一個 `\n` |
| 合計印出 `11/03,…` 一長串或 TypeError | 金額還是文字 | `total += int(amount)` |
| 來回測試印出舊的三筆 | 存檔用了 `"a"` | 整份重寫用 `"w"` |
| 第三圈「壞版本 2 沒抓到」 | 你的檢查都只有一筆 | 寫一條好幾筆的帳 |
| 第三圈「至少 1 行標『已知會當掉』」 | 還沒寫備註有逗號那一條，或沒標 | 寫一條、跑跑看，當掉了就在行尾加 `# 已知會當掉` |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-23 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、Python 官方文件的原文、Windows 的編碼怎麼確認、備註有逗號為什麼會壞）在 `補充.md`。
