# 2-4　CSV 與 JSON：匯入台灣銀行對帳單（假資料）

這課大約 55 分鐘。三圈比例 45／30／25。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：dict（1-15）、for 與 continue（1-11）、def 與 return（1-18）、import（1-21）、raise（1-22）、with open 與 encoding（1-23）、pytest（2-3）、2-1 的交辦與核准（先存檔、指令看懂才按同意）。

**練習一律用課程準備的假資料（`bank_a.csv`、`bank_b.csv`），不要拿你真的對帳單來練**，也不要把真的帳戶、卡號、交易明細貼給 AI。

1-23 留了一個問題：帳存成「用逗號隔開」的文字檔，備註裡有逗號，讀回來就壞了。這一課用 Python 內建的 **csv 模組**解決它，把設定存成 **JSON**，再匯入一份練習用的銀行對帳單：
**民國年、千分位、空白列、檔案開頭看不見的 BOM、兩家銀行的欄位名稱不一樣。**

## 1. 題目

**第①圈：自己來（csv、JSON、讀對帳單）。**

A. 先看 1-23 的問題。`ledger.txt` 是用逗號隔開存的帳，第三筆的備註是「跟小明, 小華」。在帳本資料夾跑：

```bash
uv run lessons/2-4/read_txt.py
```

印完兩筆就當掉：`ValueError: too many values to unpack`。第三行被切成五段，裝不進四個名字。

B. 用 csv 模組存（`save_csv.py`）。在「換你寫」那裡寫：

```python
with open(p, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(entries)
```

- `newline=""`：csv 模組自己處理換行（官方文件：If csvfile is a file object, it should be opened with newline=''）。Windows 上沒寫，每一行後面會多一個看不見的 `\r`，用試算表打開會多出空白列。
- `DictWriter`：每一筆是一個 dict，`fieldnames` 決定欄位的順序；`writeheader()` 先寫標題列，`writerows()` 寫每一筆。

跑完打開 `ledger.csv`：備註有逗號的那一格，被雙引號包起來了（`"跟小明, 小華"`）。

C. 讀回來（`read_csv.py`）。`csv.DictReader` 會把第一列當成欄位名稱，之後每一列變成一個 dict：

```python
with open(p, encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        print(row["日期"], row["項目"], row["金額"], row["備註"])
        total += int(row["金額"])
```

讀回來的都是文字，金額要 `int(...)`。備註的逗號照原樣回來了。

D. 設定存成 JSON（`save_settings.py`）。先跑一次，打開 `settings.json`：中文變成 `\u6bcf\u6708…` 這種代碼。在 `json.dump` 加上 `ensure_ascii=False`，再跑一次，中文就照原樣存了（官方文件：If ensure_ascii is false, all characters will be output as-is）。`json.load` 讀回來就是原本的 dict。

E. 讀練習用的對帳單（`peek.py`）。`bank_a.csv` 是課程準備的假資料（練習用的信用卡對帳單：金額是正的、退款是負的）。跑 peek.py，會跳出 `KeyError: '交易日期'`：明明有這一欄！
原因是檔案最前面有一個看不見的字 **BOM**（很多銀行、試算表匯出的 CSV 都有；VS Code 右下角寫 `UTF-8 with BOM`），第一欄的名字變成 `\ufeff交易日期`。encoding 改成 `"utf-8-sig"`，Python 會把它讀掉（官方文件：On decoding utf-8-sig will skip those three bytes）。

F. 民國年、千分位、空白列（`clean.py`、`read_bank.py`）。

- `roc_date` 已經寫好，看懂它（`re.txt` 3 題）：

```python
m = re.fullmatch(r"(\d{2,3})/(\d{1,2})/(\d{1,2})", text.strip())
```

`re` 是 Python 內建、照規則找字的模組（規則叫 regular expression）。`\d` 是一個數字，`{2,3}` 是兩到三個，括號把對到的那一段抓出來：`m.group(1)` 是 115、`m.group(2)` 是 11、`m.group(3)` 是 03。`fullmatch` 要整串都照規則才對得到，對不到就交回 None。民國年加 1911 就是西元年。

- `to_int` 換你改：`int("1,250")` 會當掉，先拿掉千分位的逗號：`return int(text.replace(",", ""))`。負號要留著，退款才是負的。
- `read_bank.py` 換你寫：bank_a.csv 裡有一列全是逗號（`,,,`），日期是空的。在 print 上面加：

```python
        if not row["交易日期"]:
            continue
```

（完全空白的一行，DictReader 自己會跳過；只有逗號的那一列，它會交給你一個每一格都是空字串的 dict。）

**第②圈：跟 AI 學（`pandas.md`）。** 問家教：「對帳單有 BOM、民國年、千分位、空白列，我用 csv 一個一個處理了。有沒有更省事的做法？」它可能會建議改用 **pandas**（一個很大的資料分析套件）。先問清楚：要另外裝嗎？會多裝哪些東西？這幾行 csv 做不到什麼？再自己決定：**這一課要不要用**，寫在 `pandas.md`（三個標籤都寫了就算交了）。

**第③圈：先寫驗收，再交給 AI。**

1. 在 `tests/test_import.py` 寫 `test_totals`：匯入 bank_a.csv 以後，各分類的合計應該是多少？**自己手算**（分類照 settings.json 的分類關鍵字；退款是負的，要扣掉）：

```python
def test_totals():
    entries = import_statement(FOLDER / "bank_a.csv", KEYWORDS)
    totals = category_totals(entries)
    assert totals == {"餐飲": 185, …}   # 其他幾類自己算
```

在帳本資料夾打 `uv run pytest lessons/2-4`（只跑這一課的測試）。現在會紅：import_bank.py 還沒寫。這是對的，先紅後綠（2-3）。

2. 先按存檔點（原始碼控制面板，說明寫「交辦前」）。
3. 在 Chat 選 Agent，交辦四欄：

> 目標：寫 lessons/2-4/import_bank.py，有 import_statement(path, keywords) 和 category_totals(entries)。import_statement 讀一份對帳單（CSV），交回一串 (日期, 項目, 分類, 金額)。
> 背景：bank_a.csv、bank_b.csv 是兩家銀行的樣本（假資料），欄位名稱不一樣（交易日期／消費日、摘要／說明、金額／交易金額）；檔案開頭可能有 BOM；日期是民國年（115/11/03 要變成 2026/11/03）；金額有千分位；退款是負的；有空白列。分類照 keywords（項目裡有哪個關鍵字就是哪一類，都沒有是「其他」）。
> 限制：只用 Python 內建的 csv、json、re，不要裝任何套件；不要改 tests 資料夾。
> 怎樣算做完：uv run pytest lessons/2-4 全部通過，把輸出貼給我。

4. 它要執行指令時會先問你，一個一個看懂再按同意。它沒附 pytest 的輸出，就不算做完。
5. 自己再跑一次 `uv run pytest lessons/2-4`。沒過就看是哪一類的合計不對，打開 import_bank.py 找原因，改好再跑。
6. 跑檢查：`uv run check.py 2-4` 還會拿幾份**你沒看過的對帳單**（另一家銀行的欄位、Windows 的換行、更多空白列）試你的 import_bank.py。
7. 決定收不收，寫在 `decision.md`。收了，再按一個存檔點（說明寫「匯入對帳單」）。

沒開 GitHub 帳號的同學：在帳本資料夾打 `cp lessons/2-4/ai_import_bank.py lessons/2-4/import_bank.py`（課程凍結的一份 AI 版本），從第 5 步做起（也可以把交辦的話貼給聊天版 AI，把它寫的程式貼進去）。

**選做加深：發票載具匯入。** 手機條碼載具的消費明細，在財政部的電子發票平台查得到（能不能下載、是什麼格式，照平台當時的頁面為準）。照同樣的做法：先看檔案長什麼樣子（欄位、日期、金額），自己編一份同樣格式的假資料樣本、手算合計寫成測試，再交給 AI。check 不考，也不要拿你真的明細練習。

## 2. 提示

- **csv 會幫你加雙引號：** 一格裡有逗號、雙引號或換行，csv 模組存的時候會用雙引號包起來，讀的時候再拿掉。自己用逗號接字串、用 split(",") 切，就會像 1-23 一樣壞掉。
- **讀回來的都是文字：** DictReader 給你的每一格都是字串，`"120"` 要 `int(...)` 才能加。
- **ensure_ascii：** 預設是 True，中文會存成 `\u9910` 這種代碼（讀回來還是對的，只是人看不懂）。設定檔要給人看，就寫 `ensure_ascii=False`，open 也要寫 `encoding="utf-8"`。
- **BOM：** 檔案最前面三個看不見的位元組，用來表示「這是 UTF-8」。用 `encoding="utf-8-sig"` 打開：有 BOM 就讀掉，沒有也照常讀。
- **千分位與負號：** `"1,250".replace(",", "")` 是 `"1250"`。不要用 `re.sub(r"\D", "", …)` 拿掉「不是數字的字」：負號也不是數字，退款會變成支出。
- **對不到的日期：** `re.fullmatch` 對不到交回 None，`roc_date` 會丟出 `ValueError: 看不懂的日期`。看到它，先看那一列的日期長什麼樣子。
- **為什麼不用 pandas：** pandas 很好用，但它是一個很大的套件：uv add pandas 會連 numpy、python-dateutil、tzdata 一起裝，.venv 多了大約 70 MB（2026-11 沙盒實測），我們也還沒學。這一課的檔案只有幾十行，Python 內建的 csv 就做得到。
- **第 2 級交辦給 agent 的三條規矩：** 它不能改 `tests/`、不能用 pip 裝套件、沒附測試的輸出不算做完。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 2-4
```

它會把起點檔複製到你的帳本 `lessons/2-4/`：`ledger.txt`、`read_txt.py`、`save_csv.py`、`read_csv.py`、`save_settings.py`、`bank_a.csv`、`bank_b.csv`（兩份都是假資料）、`peek.py`、`clean.py`、`read_bank.py`、`re.txt`、`pandas.md`、`ai_import_bank.py`、`conftest.py`、`tests/test_import.py`、`decision.md`。

用 VS Code 打開帳本，在下面的終端機（帳本資料夾）打第 1 節的指令，例如：

```bash
uv run lessons/2-4/save_csv.py
uv run lessons/2-4/read_csv.py
uv run lessons/2-4/save_settings.py
uv run lessons/2-4/peek.py
uv run lessons/2-4/read_bank.py
uv run pytest lessons/2-4
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 2-4
```

## 4. 成品示範

```
$ uv run lessons/2-4/read_csv.py
11/03 午餐 120 跟同事
11/04 公車 15
11/05 聚餐 600 跟小明, 小華
合計 735 元
$ uv run lessons/2-4/read_bank.py
2026/11/01 早餐店 65
2026/11/02 捷運加值 500
2026/11/03 超市 1250
2026/11/05 電影院 320
2026/11/06 超市退款 -350
2026/11/08 便當店 120
```

`ledger.csv`（在 VS Code 左邊的檔案總管點開）：

```
日期,項目,金額,備註
11/03,午餐,120,跟同事
11/04,公車,15,
11/05,聚餐,600,"跟小明, 小華"
```

## 5. 怎麼測

`uv run check.py 2-4` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。check 在系統的暫存資料夾裡跑你的程式，不會動你帳本裡的檔案。

第一圈：ledger.csv 的內容（標題列、雙引號）、read_csv.py 印出三筆和合計、settings.json 的中文照原樣存、peek.py 讀得到「交易日期」、to_int 兩題、read_bank.py 六筆、re.txt 3 題；第二圈：pandas.md 三個標籤寫了沒；第三圈：你的 test_import.py 在正確版上全過、抓得到兩個壞版本（退款當成支出、退款整筆不見）；你的 import_bank.py 匯入三份你沒看過的對帳單（隱藏的髒資料）、category_totals；交辦前先存檔、decision.md。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `ValueError: too many values to unpack` | 用 split(",") 切，備註的逗號多切了一段 | 改用 csv 模組 |
| `KeyError: '交易日期'` | 檔案開頭有 BOM，第一欄的名字變成 `\ufeff交易日期` | encoding 改成 `"utf-8-sig"` |
| `ValueError: invalid literal for int() with base 10: '1,250'` | 金額有千分位 | `int(text.replace(",", ""))` |
| `ValueError: 看不懂的日期：` | 空白列的日期是空的 | 日期是空的就 continue |
| settings.json 裡是 `\u6bcf\u6708` | 少了 ensure_ascii=False | `json.dump(settings, f, ensure_ascii=False, indent=2)` |
| 試算表打開 ledger.csv 每一行中間多一行空白 | open 少了 `newline=""`（Windows） | 寫 csv 的 open 都加 `newline=""` |
| pytest：`'日用品': 1600` 不等於 `900` | 退款被當成支出（負號被拿掉） | 拿掉千分位只拿逗號：`replace(",", "")` |
| `ModuleNotFoundError: No module named 'import_bank'` | import_bank.py 還沒寫 | 第③圈請 AI 寫，或複製 ai_import_bank.py |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「2-4 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的對話、Python 官方文件的原文、發票載具的做法）在 `補充.md`。
