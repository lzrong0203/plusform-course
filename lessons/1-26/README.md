# 1-26　讀別人的程式：100 行陌生程式加一個功能

這課大約 45 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl、⇧⌥F12 換成 Shift＋Alt＋F12（安裝見 0-W）。
要會的：函式（1-18）、預設值和關鍵字參數（1-19）、模組與 import（1-21）、例外處理（1-22）、檔案讀寫（1-23）、class 和 @dataclass（1-24）、移至定義和尋找所有參考（1-25）。

## 1. 題目

**第①圈：關掉 AI 讀一支陌生程式，再加一個功能。**

`old_ledger.py` 是熊的舊記帳程式，大約一百行，寫法跟這門課不太一樣。跑起來以後打指令：`show` 列出每一筆、`add 11/06 咖啡 85` 記一筆、`total` 合計、`q` 離開。帳存在旁邊的 `old_ledger.txt`。

A. 先畫呼叫圖（在紙上就好）：從最下面的 `if __name__ == "__main__":` 開始，main 呼叫了誰、那個函式又呼叫了誰，一層一層往下畫。讀的時候可以跑它、可以用移至定義（F12）和尋找所有參考（⇧⌥F12），不要問 AI。畫完在 `read.txt` 答 10 題。

B. 加上 `delete` 指令：打 `delete 2`，刪掉 `show` 印的第 2 筆，存回檔案。照 `add` 的樣子寫在 `total` 下面：

- 上面寫 `@command`，它才會被放進 `COMMANDS`、main 才找得到；
- `arg` 是打進來的字（例如 `"2"`），先用 `int(arg)` 變成數字；
- `show` 的編號從 1 開始，list 的索引從 0 開始；
- 刪完呼叫 `save(entries)` 存回檔案。

跑起來要像這樣（打 show、delete 2、show）：

```
> show
1. 11/03 午餐 120
2. 11/04 公車 15
3. 11/05 晚餐 180
> delete 2
刪掉了： 2. 11/04 公車 15
> show
1. 11/03 午餐 120
2. 11/05 晚餐 180
```

**第②圈：請家教出 3 題「這段在做什麼」考你（`tutor.md`）。** 貼上整份 `old_ledger.py`，請它挑最難懂的三段各出一題，先自己答、再請它批改；答錯的那一題，回 VS Code 自己對照一次。

**第③圈：需求寫進 docstring，交給 AI，再驗收。** 熊想把刪除改得安全一點：「刪除前要先確認」。他把需求寫成 `delete_entry` 的 docstring：

> 刪掉第 no 筆（no 跟 show 印的編號一樣，從 1 開始），刪除前要先確認：confirm 是 False（沒寫就是 False）只交回要刪的那一筆、不刪；是 True 才從 entries 拿掉，也交回那一筆。編號不在 1 到筆數之間：丟 ValueError，什麼都不刪。

`delete_ai.py` 是 AI 交回來的版本（課程準備的固定版本，範例示意，不要改它）。在 `checks_delete.py` 寫 assert 驗收（至少 3 條）：你的檢查要在正確的版本上全部成立、在課程藏的 3 個 AI 寫錯的版本上至少有一條不成立。想想 AI 最容易寫錯哪裡：刪掉的是不是那一筆？沒確認的時候真的沒刪嗎？編號 0 呢？

跑你的 `checks_delete.py` 時，**出現 AssertionError 是對的**：`delete_ai.py` 這一版刪錯了一筆，你的檢查抓到了。check 會拿你的檢查去跑課程準備的正確版和 3 個壞版本。

## 2. 提示

- **從哪裡讀起：** 不要從第 1 行一路讀到最後。上面的 `import`、`def`、`class` 只是先把東西記下來，最下面的 `main()` 一呼叫，程式才開始做事。從 main 往下追「誰呼叫了誰」，畫成呼叫圖；看不懂的那一行先猜大意，用到再查。
- **`@command`（decorator，看得懂就好）：** 寫在 `def` 上面的 `@名字`，等於在那一段後面多寫一行 `show = command(show)`：把下面的函式交給 command 處理一次（官方術語表：merely syntactic sugar）。這支程式的 command 把函式用名字放進 `COMMANDS` 這個 dict，所以 main 用 `COMMANDS[name](entries, arg)` 就呼叫得到。對 `show` 按「尋找所有參考」，找不到別人呼叫它，原因就在這裡。1-24 的 `@dataclass` 也是一種 decorator。
- **`yield`（generator，看得懂就好）：** 有 `yield` 的函式，一次交出一個值、停在那裡；要下一個的時候，從停下來的地方接着跑（官方術語表：picks up where it left off）。`list(read_entries(DATA))` 會一直要下一筆，直到檔案讀完。
- **`re`（看得懂就好）：** `re.compile(r"(\d+/\d+) (\S+) (\d+)")` 是在描述「一行長什麼樣子」：`\d` 是一個數字、`+` 是一個以上、`\S` 是一個不是空白的字，括號圍起來的三段可以用 `m.group(1)`、`group(2)`、`group(3)` 拿出來。`fullmatch` 要整行都對得上，對不上交回 None。
- **`logging`（看得懂就好）：** 比較正式的 print，會標等級。`logging.warning(...)` 印出 `WARNING:root:…`；`logging.info(...)` 沒有另外設定時不會印（官方 HOWTO：The default level is WARNING）。看到 WARNING 開頭的那一行，不是程式當掉，是它在提醒你。
- **編號和索引差一：** `show` 用 `enumerate(entries, start=1)` 編號，第 2 筆是 `entries[1]`。寫成 `entries.pop(no)` 會刪到下一筆；編號 0 時 `entries.pop(0 - 1)` 是 `pop(-1)`，會刪到最後一筆。
- **刪除前要先確認：** 刪錯了沒辦法反悔。先把要刪的那一筆交回來給人看，確認了才真的刪：差一的版本，在確認那一步就看得出「這不是我要刪的」。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-26
```

它會把起點檔複製到你的帳本 `lessons/1-26/`：`old_ledger.py`、`old_ledger.txt`、`read.txt`、`tutor.md`、`delete_ai.py`（AI 交回的版本，不要改）、`checks_delete.py`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-26/old_ledger.py
uv run lessons/1-26/checks_delete.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-26
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-26`。）

## 4. 成品示範

```
$ uv run lessons/1-26/old_ledger.py
可以打的指令：show、add、total、delete、q
> add 11/06 咖啡 八十五
WARNING:root:看不懂：11/06 咖啡 八十五
> delete 2
刪掉了： 2. 11/04 公車 15
> total
合計 300 元
> q
$ uv run lessons/1-26/checks_delete.py
Traceback (most recent call last):
  ...
AssertionError
```

`checks_delete.py` 跑 AI 交回的 `delete_ai.py` 出現 AssertionError，就是你的檢查抓到它刪錯了。

## 5. 怎麼測

`uv run check.py 1-26` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。

第一圈：`read.txt` 10 題、**delete 指令**（check 把你的 old_ledger.py 和課程原本的三筆帳放進暫存資料夾，打 show、delete 2、show，看第 2 筆公車有沒有不見；你的 old_ledger.txt 不會被動到）、**delete 刪對、存檔**（另外擺三筆帳，刪第 2 筆兩次，看剩下哪幾筆、檔案裡存了什麼）；第二圈：`tutor.md` 四個標籤寫了沒；第三圈：你的檢查抓不抓得到 3 個 AI 寫錯的 delete_entry。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `沒有這個指令： delete` | delete 上面少了 `@command`，沒放進 COMMANDS | 在 `def delete` 上面一行寫 `@command` |
| 刪掉的是第 3 筆 | 寫成 `entries.pop(no)`，編號當成索引 | 改成 `entries.pop(no - 1)` |
| `IndexError: pop index out of range` | 同上，刪最後一筆時超出範圍 | 改成 `entries.pop(no - 1)` |
| `TypeError: 'str' object cannot be interpreted as an integer` | `arg` 是字，沒有先變成數字 | `no = int(arg)` |
| 刪了，下次打開又回來了 | 刪完沒有存檔 | 最後加 `save(entries)` |
| `WARNING:root:invalid literal for int() with base 10: ''` | 只打了 delete，後面沒有編號 | 打 `delete 2` |
| 第三圈「壞版本 1 沒抓到」 | 你只看少了一筆，沒看刪掉的是哪一筆 | `assert delete_entry(book, 2) == bus` |
| 第三圈「壞版本 3 沒抓到」 | 沒有試編號 0 | 用 try／except ValueError 寫一條 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-26 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、Python 官方文件的原文、自評兩題：畫出呼叫圖、用一句話講每個函式在做什麼）在 `補充.md`。
