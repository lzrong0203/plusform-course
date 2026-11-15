# 1-16　可變與參照：為什麼你的 list 自己變了

這課大約 45 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：變數與等號（1-2）、比較與 assert（1-8）、list 的索引、切片、`append`、`sum`（1-13）、tuple 不能改（1-14）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 不能改裡面的型別（`predict.txt`）：3 題，先不要跑，用眼睛追。

B. 用 `is` 檢查是不是同一個（`ids.py`）。上面三行 `a = [120, 85]`、`b = a`、`c = a.copy()` 不要改，在下面寫三行 `print`：

1. a 和 b 是不是同一個 list（用 `is`）
2. a 和 c 是不是同一個 list（用 `is`）
3. a 和 c 裡面的值一不一樣（用兩個等號）

C. 果凍兔的兩本帳本（`ledgers.py`）。熊和兔想各記各的，都從 `start = []` 開始，可是跑起來兩本一模一樣。改 `bear`、`rabbit` 那兩行，讓熊的只有 120、兔的只有 300，最後一行印出 `是同一本嗎 False`。

**第②圈：請家教考你「最後 a 是什麼」，每一題先畫圖（`tutor.md`、`final_a.txt`）。** 在家教專案裡請它一次問一題、每題用三四行的短程式，**每一題都要你先用文字畫圖**（哪個名字指著哪個盒子），再回答最後 a 是什麼，**先不要給答案**。家教說你哪裡不對，自己跑一次，確定它說得對不對（AI 也會看錯）。記在 `tutor.md`（自評，不擋過關）。`final_a.txt` 有四題同樣的題型。

**第③圈：先寫 assert 證明它錯，再修好（`checks_budget.py`、`budget.py`）。** AI 寫了一支兩個月的預算 `budget.py`（課程準備的版本，範例示意）：固定開銷 `fixed` 是房租 12000、手機 499，11 月 `nov` 再加午餐 120，12 月 `dec` 再加機票 3000，最後印出 11 月合計、12 月合計、固定開銷。它跑得起來、沒有錯誤訊息，**可是算錯了**。照兩步做：

1. **先證明它錯**：先自己算好正確答案，在 `checks_budget.py` 寫至少一條 assert（右邊放你算好的數字）。在帳本資料夾跑 `uv run lessons/1-16/checks_budget.py`，跳出 `AssertionError`，就證明 `budget.py` 算錯了。
2. **再修好**：改 `budget.py`，讓 nov、dec 各自從 fixed 複製一份（`fixed.copy()` 或 `fixed[:]`），fixed 本身不能被改到。再跑一次 `checks_budget.py`，同一條 assert 要變成成立（什麼錯誤都沒有）。

```python
from budget import fixed, nov, dec

# 11 月：固定開銷加午餐
assert sum(nov) == ……（你自己算好的數字）
```

`uv run check.py 1-16` 會把你的 `checks_budget.py` 拿去跑課程的正確版和三個算錯的版本（第 1 個就是你拿到的那一支 `budget.py`，另外兩個是只修好一半的），正確版上要全部成立、每個算錯的版本至少要有一條不成立；再跑你修好的 `budget.py`，看三行印得對不對。

## 2. 提示

- **名字指著盒子。** `a = [120, 85]` 是先做出一個 list（一個盒子），再把名字 a 指著它。**`b = a` 不會複製**，只是讓名字 b 也指著同一個盒子（官方 FAQ：Doing y = x doesn't create a copy of the list）。名字指向一個東西，叫做**參照**。
- 兩個名字指著同一個 list 時，從其中一個改裡面（`b.append(95)`、`b[0] = 0`、`b.remove(85)`），從另一個看也變了，因為盒子只有一個。
- **`id(a)`** 交回一個整數，代表這個物件是誰：同一個時間裡，不同的物件不會拿到一樣的數字（官方文件：unique and constant for this object during its lifetime）。數字每次跑都不一樣，只拿來比「一不一樣」。
- **`a is b`** 問 a 和 b 是不是同一個物件（跟 `id(a) == id(b)` 一樣）；**`a == b`** 問的是裡面的值一不一樣。兩個複製出來的 list，`==` 是 True，`is` 是 False。
- **複製一份**：`b = a.copy()` 或 `b = a[:]`（1-13 學過，切出來的是一串新的），都會做出第二個盒子。之後改 b，a 不會變。
- **copy() 和 [:] 只複製最外面一層。** list 裡面又放 list（例如一週七天、每天三餐的預算表），複製出來的外層是新的，裡面那幾個小 list 還是同一個；改 `b[0].append(5)`，a 也看得到。要連裡面一起複製，用 `copy.deepcopy`（`import` 到 1-21 才教，例子在補充.md）。
- **等號只是把名字換過去。** `b = [300]`、`b = b + [95]`：右邊先算出一個新的 list，再把名字 b 指過去，原本的盒子沒被改，a 不會變。（`b += [95]` 不一樣，它會直接改原本的盒子，見補充.md。）
- **可變與不可變**：list、dict、set 可以直接改裡面（可變，mutable）；int、str、tuple 不能改裡面（不可變，immutable），`x = x + 1`、`s = s + "便當"` 都是做出一個新的、再把名字換過去，所以另一個指著舊的名字不會變。
- 不確定兩個名字是不是同一個，就印 `a is b` 看一下。
- 第③圈：assert 右邊寫**你自己算好的正確答案**。右邊寫「跟另一個算出來的比」（例如 `sum(nov) == sum(dec)`），錯的版本上反而成立，證明不了它錯。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-16
```

它會把起點檔複製到你的帳本 `lessons/1-16/`：`predict.txt`、`ids.py`、`ledgers.py`、`final_a.txt`、`tutor.md`、`budget.py`（AI 寫的、算錯的那一支，第③圈要修）、`checks_budget.py`，還有影片裡熊在 VS Code 打的 `two.py`（第 2、5 行空著，可以跟著打一次；check 不檢查）。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-16/ids.py
uv run lessons/1-16/ledgers.py
uv run lessons/1-16/checks_budget.py
uv run lessons/1-16/budget.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-16
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-16`。）

## 4. 成品示範

```
$ uv run lessons/1-16/ids.py
True
False
True
$ uv run lessons/1-16/ledgers.py
熊的帳 [120]
兔的帳 [300]
是同一本嗎 False
```

第③圈，修好以前先證明它錯：

```
$ uv run lessons/1-16/checks_budget.py
11 月合計 15619 元
12 月合計 15619 元
固定開銷 15619 元
Traceback (most recent call last):
  ...
AssertionError
```

修好以後：

```
$ uv run lessons/1-16/checks_budget.py
11 月合計 12619 元
12 月合計 15499 元
固定開銷 12499 元
```

（`checks_budget.py` 用到 `budget.py` 時，`budget.py` 會先跑一次、印出它的三行；後面沒有錯誤訊息，代表每一條 assert 都成立。）

## 5. 怎麼測

`uv run check.py 1-16` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。一共 19 題：

- 第一圈：`predict.txt` 3 題、`ids.py` 2 題（原本的跑一次；check 把 `c = a.copy()` 換成 `c = a` 再跑一次）、`ledgers.py` 2 題（一樣跑兩次，第二次熊記的換成 65）
- 第二圈：`final_a.txt` 4 題
- 第三圈：至少寫 1 條 assert、在正確版上全部成立、抓到 3 個算錯的版本（5 題）；`budget.py` 修好了（2 題：原本的跑一次，check 把 fixed 換成別的金額再跑一次）；修好以後，你的 `checks_budget.py` 在你的 `budget.py` 上全部成立（1 題）

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。`tutor.md` 是自評，check 不檢查。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| ledgers.py 兩本都印 `[120, 300]` | bear、rabbit、start 三個名字指著同一個 list | `bear = start.copy()`、`rabbit = start.copy()`（或各自寫 `[]`） |
| ids.py 第二題印 `False` | 直接寫了 `print(False)`，或用了兩個等號 | 用 `print(a is c)`：c 換成 `c = a` 以後要印 True |
| 跑 `checks_budget.py` 跳出 `AssertionError` | budget.py 還沒修好（第一步就是要看到它），或你算的答案寫錯了 | 修好 budget.py 再跑；還是不成立，就重新算一次右邊的數字 |
| 第③圈「這條在正確版上不成立」 | assert 右邊的答案算錯了 | 正確版：固定開銷 12000＋499、11 月再加 120、12 月再加 3000 |
| 第③圈「抓到 1 個，還有 2 個溜過去」 | 只檢查了一個月的合計 | 照提示看：固定開銷 fixed 本身有沒有被改到？12 月的合計對嗎？ |
| budget.py 第二題沒過，可是第一題過了 | nov、dec 是把 12000、499 再打一次，不是從 fixed 複製 | `nov = fixed.copy()`、`dec = fixed.copy()` |
| `ModuleNotFoundError: No module named 'budget'` | `budget.py` 不在 `checks_budget.py` 同一個資料夾 | 在課程資料夾打 `uv run check.py start 1-16`，它會把 `budget.py` 複製過去 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-16 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、Python 官方文件的原文、`id()` 是什麼、`+=` 為什麼會改原本的 list、list 裡面放 list 的淺複製、第③圈三個算錯的版本各錯在哪）在 `補充.md`。
