# 1-14　tuple、set 與拆包

這課大約 50 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：`print`、變數與等號（1-2）、`type`（1-3）、比較與 assert（1-8）、`for` 與 `enumerate`（1-11）、list、`sorted`（1-13）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. tuple 和拆包預測（`predict.txt`）：4 題，先不要跑，用眼睛追。

B. 一筆帳拆成三個名字（`record.py`）。`record = ("11/03", "午餐", 120)` 是一筆帳：日期、項目、金額。照兩步寫：

1. 用一行拆包，把 record 拆成 `date`、`item`、`amount` 三個名字
2. 印出「11/03 午餐 120 元」

C. 一行交換（`swap.py`）：`a = 3`、`b = 5`，在空著的那一行用一行拆包把兩個交換，印出 `5 3`。

D. 兩個月的分類（`kinds.py`）。`nov`、`dec` 是 11 月、12 月每一筆帳的分類，同一個分類會出現好幾次。照三步寫：

1. 印出「11 月一共 6 筆，花在 3 種分類」：筆數用 `len(nov)`，分類數先用 `set` 去掉重複再算 `len`
2. 印出「兩個月都有 ['交通', '餐飲']」：兩個 set 取交集 `&`，再用 `sorted` 排好
3. 印出「只有 11 月有 ['娛樂']」：差集 `-`，一樣用 `sorted` 排好

**第②圈：請家教考你，一筆帳該用 tuple 還是 list（`tutor.md`、`set_quiz.txt`）。** 在家教專案裡請它一次問一題、等你回答再追問，**先不要給答案**。每一題先自己想、寫下答案再貼給它；它說你哪裡不對，自己跑一次，確定它說得對不對。記在 `tutor.md`（自評，不擋過關）。`set_quiz.txt` 有四題 set 的順序。

**第③圈：用註解和 assert 寫下需求，驗收 AI 寫的分類小工具（`checks_months.py`）。** 需求卡：

| 欄 | 內容 |
|---|---|
| 目標 | 找出兩個月都有花錢的分類：`both_months(nov, dec)` |
| 背景 | `nov`、`dec` 是兩個月每一筆帳的分類，同一個分類會出現好幾次 |
| 限制 | 每個分類只出現一次；**排好序**（用 `sorted` 排，交回的是 list） |
| 怎樣算做完 | 用註解寫下要求、用 assert 寫下一定要成立的事（至少 5 條），在正確版上全部成立，三個壞版本各被至少一條抓到 |

AI 照這張需求卡寫了 `months.py`（課程凍結的版本：正確版在 `reference/`，三個壞版本在 `mutants/`）。你**不用看懂它的程式**（`def` 到 1-18 才教），只要在 `checks_months.py` 裡**呼叫**它，每一段先寫一行註解說要檢查什麼，下面寫 assert：

```python
from months import both_months

# 兩個月都有交通
nov = ["餐飲", "交通", "餐飲", "娛樂"]
dec = ["交通", "醫療", "餐飲", "交通"]
assert "交通" in both_months(nov, dec)
```

`uv run check.py 1-14` 會把你的 `checks_months.py` 拿去跑正確版和三個壞版本（每個版本各跑一次、互不影響），正確版上要全部成立，每個壞版本至少要有一條不成立。

## 2. 提示

- **tuple** 是一串用逗號隔開、通常用圓括號包起來的東西：`record = ("11/03", "午餐", 120)`。跟 list 一樣用索引拿（`record[0]` 是第一個），也可以用 `len`。
- **tuple 放進去就不能改**：`record[2] = 90` 會出現 `TypeError: 'tuple' object does not support item assignment`。記錯了就整筆換掉：`record = ("11/03", "午餐", 90)`（名字 record 拿到一個新的 tuple）。
- 只有一個值的 tuple，後面要加逗號：`(120,)`。只寫 `(120)` 是加了括號的整數 120。
- **拆包**：`date, item, amount = record`，照順序一個對一個放進左邊的名字。左邊的個數要跟右邊一樣，不一樣會出現 `ValueError`（too many values／not enough values to unpack）。
- **交換**：`a, b = b, a`。右邊先算好（拿出 b 和 a 的值），再一起放進左邊，所以不用多一個暫放的名字。先寫 `a = b` 再寫 `b = a`，兩個會變成一樣。
- `for date, item, amount in records:`：一串帳裡每一筆都是 tuple，for 拿出來的同時拆包。1-11 的 `for day, cost in enumerate(week):` 也是這樣，enumerate 每一圈給的是 (編號, 那一個) 的 tuple。
- **set**：一袋**不重複**的東西。`set(kinds)` 把 list 裡重複的拿掉；也可以用大括號寫 `{"餐飲", "交通"}`。空的 set 要寫 `set()`（`{}` 是 1-15 才教的 dict）。
- set 可以用 `in` 問有沒有、用 `len` 算有幾種、用 `add` 加一個（已經有的再加一次，不會變多）。**set 沒有索引**（`s[0]` 會出現 `TypeError`）。
- 兩個 set 的運算：`a & b` 交集（兩邊都有）、`a | b` 聯集（任何一邊有）、`a - b` 差集（a 有、b 沒有）。
- **set 沒有保證順序**。印出來的先後只是剛好，同一支程式跑兩次可能不一樣；小的整數像 `{3, 1, 2}` 常常剛好印成 `{1, 2, 3}`，那也只是剛好（`{30, 120, 85}` 會印出 `{120, 85, 30}`）。**要固定的順序，用 `sorted`，它交回一個排好的 list。** set 沒有 `sort()`。
- 中文用 `sorted` 排，是照電腦裡每個字的編號排，不是注音也不是筆畫：`sorted(["餐飲", "交通", "娛樂"])` 是 `['交通', '娛樂', '餐飲']`。
- 第③圈：需求說排好序，assert 就要拿整串排好的 list 用兩個等號比：`assert r == ["交通", "餐飲"]` 是在問「r 是不是這兩個、而且是這個順序、而且是 list」。只用 `in`、`not in`、`len` 檢查，抓不到「答案對、可是沒排好」的版本。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-14
```

它會把起點檔複製到你的帳本 `lessons/1-14/`：`predict.txt`、`record.py`、`swap.py`、`kinds.py`、`set_quiz.txt`、`tutor.md`、`months.py`（課程版本，不用改）、`checks_months.py`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-14/record.py
uv run lessons/1-14/swap.py
uv run lessons/1-14/kinds.py
uv run lessons/1-14/checks_months.py
```

`checks_months.py` 跑起來什麼都沒印，代表每一條 assert 在正確版上都成立。檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-14
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-14`。）

## 4. 成品示範

```
$ uv run lessons/1-14/record.py
11/03 午餐 120 元
$ uv run lessons/1-14/swap.py
5 3
$ uv run lessons/1-14/kinds.py
11 月一共 6 筆，花在 3 種分類
兩個月都有 ['交通', '餐飲']
只有 11 月有 ['娛樂']
```

第③圈只用 in、not in、len 檢查時，check 會說：

```
你的檢查抓到 2 個壞版本，還有 1 個溜過去：
  ・需求說排好序：交回的是排好的 list 嗎？
```

## 5. 怎麼測

`uv run check.py 1-14` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。一共 19 題：

- 第一圈：`predict.txt` 4 題、`record.py` 2 題（原本的 record 跑一次；check 把 record 換成別的一筆再跑一次）、`swap.py` 2 題、`kinds.py` 2 題（一樣跑兩次）
- 第二圈：`set_quiz.txt` 4 題
- 第三圈：至少寫 5 條 assert、在正確版上全部成立、抓到 3 個壞版本。寫滿 5 條以前，只告訴你抓到幾個，不告訴你溜過去的是哪一種

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。`tutor.md` 是自評，check 不檢查。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `TypeError: 'tuple' object does not support item assignment` | 想改 tuple 裡的某一個 | tuple 不能改；整筆換掉：`record = (日期, 項目, 新的金額)` |
| `ValueError: too many values to unpack` | 拆包時左邊的名字比右邊少 | 左邊寫三個名字：`date, item, amount = record` |
| swap.py 印出 `5 5` | 先寫 `a = b` 再寫 `b = a`，a 原本的值被蓋掉了 | 用一行：`a, b = b, a` |
| kinds.py 印出大括號 `{'餐飲', '交通'}` | 印的是 set，沒有排序 | 用 `sorted(...)` 排好，拿到方括號的 list |
| `TypeError: 'set' object is not subscriptable` | 想用索引拿 set 的第幾個 | set 沒有索引；要用索引就先 `sorted(...)` 變成 list |
| `AttributeError: 'set' object has no attribute 'sort'` | set 沒有 sort() | 用 `sorted(s)` |
| 第③圈「這條在正確版上不成立」，正確版交回 `['交通', '餐飲']` | 跟大括號的 set 比，或先後寫反了 | 正確版交回的是 list：寫成 `== ["交通", "餐飲"]`（照 sorted 排出來的順序） |
| `ModuleNotFoundError: No module named 'months'` | 自己試跑時，`months.py` 不在同一個資料夾 | 在課程資料夾打 `uv run check.py start 1-14`，它會把 `months.py` 複製過去 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-14 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、Python 官方文件的原文、set 的順序為什麼每次不一樣、第③圈三個壞版本各錯在哪）在 `補充.md`。
