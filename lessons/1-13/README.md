# 1-13　list：一串帳目

這課大約 50 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：`print`、變數（1-2）、比較與 assert（1-8）、`for`、`range`、`enumerate`（1-11，那時候方括號先當成「一串數字」，這一課正式講）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 索引預測（`index.txt`）：4 題，先不要跑，用眼睛追。可以在紙上畫一排格子，格子下面標索引。

B. 一串帳目（`ledger.py`）。`amounts = [120, 85, 200, 95]` 照記帳的先後順序放了四筆。照三步寫：

1. 在最後面加一筆 150（`append`）
2. 印出「一共 5 筆，合計 650 元」：筆數用 `len`、合計用 `sum`
3. 印出「第一筆 120 元，最後一筆 150 元」：用索引拿，最後一筆用負的索引

C. 改帳目（`fix.py`）：漏記的 60 用 `insert` 插在索引 1；記錯的 85 用 `remove` 刪掉；最後一筆用 `pop` 拿出來放進 `last`；印出 `last` 和剩下的 `amounts`。一行做一件事，不要整串重寫。

D. 排序，原本的也留著（`sort.py`）：印出由小到大排好的樣子，再印出原本的順序。`sort()` 和 `sorted()` 選一個不會動到原本 list 的。

**第②圈：請家教追問你 sort 和 sorted 差在哪（`tutor.md`、`sort_quiz.txt`）。** 在家教專案裡請它一次問一題、用很短的程式問你會印出什麼，**先不要給答案**。每一題先自己想、寫下答案再貼給它；它說你錯的那一題，自己跑一次，確定它說得對不對。記在 `tutor.md`（自評，不擋過關）。`sort_quiz.txt` 有三題同樣的題型。

**第③圈：用註解和 assert 寫下需求，驗收 AI 寫的帳目小工具（`checks_list.py`）。** 需求卡：

| 欄 | 內容 |
|---|---|
| 目標 | 兩個帳目小工具：`remove_last` 刪掉最後一筆、`index_of_max` 找出最大的一筆在第幾個位置 |
| 背景 | 帳目照記帳的先後順序存在 list 裡，之後還要照這個順序刪、照這個順序查 |
| 限制 | `remove_last` 交回被刪掉的那一筆；`index_of_max` 交回索引（從 0 數），一樣大的交回前面那一筆；**查最大的時候，不能動到原本的順序** |
| 怎樣算做完 | 用註解寫下要求、用 assert 寫下一定要成立的事（至少 5 條），在正確版上全部成立，三個壞版本各被至少一條抓到 |

AI 照這張需求卡寫了 `entries.py`（課程凍結的版本：正確版在 `reference/`，三個壞版本在 `mutants/`）。你**不用看懂它的程式**（`def` 到 1-18 才教），只要在 `checks_list.py` 裡**呼叫**它，每一段先寫一行註解說要檢查什麼，下面寫 assert：

```python
from entries import remove_last, index_of_max

# 刪掉最後一筆：交回那一筆
a = [120, 85, 200]
assert remove_last(a) == 200
```

`uv run check.py 1-13` 會把你的 `checks_list.py` 拿去跑正確版和三個壞版本（每個版本各跑一次、互不影響），正確版上要全部成立，每個壞版本至少要有一條不成立。

## 2. 提示

- list 是一串放在方括號裡、用逗號隔開的東西，有先後順序。**索引從 0 開始數**：`amounts[0]` 是第一筆，`amounts[1]` 是第二筆。
- 負的索引從後面數回來：`amounts[-1]` 是最後一筆，`amounts[-2]` 是倒數第二筆。索引超出範圍（四筆卻寫 `amounts[4]`）會出現 `IndexError: list index out of range`。
- `len(amounts)` 是有幾筆；`sum(amounts)` 是全部加起來（1-11 自己寫的累加，Python 有現成的）；`85 in amounts` 問 85 在不在裡面，交回 `True` 或 `False`。
- 切片 `amounts[1:3]`：從索引 1 開始，到 3 之前停，**3 那一格不算**（跟 `range` 一樣）。冒號前面空著是從頭開始（`amounts[:2]`），後面空著是一直拿到最後（`amounts[2:]`）。切出來的是一串新的，原本的不變。
- 改 list 的四個：`append(x)` 加在最後面；`insert(i, x)` 插在索引 i，原本在 i 和後面的都往後挪一格；`remove(x)` 刪掉**第一個等於 x** 的那一筆（括號裡寫的是值，不是索引；找不到會出現 `ValueError`）；`pop()` 拿走最後一筆、**還會交回它**，`pop(0)` 拿走第一筆。
- 改過 list 以後，後面的索引會跟著變：插一筆，後面每一筆的索引都加 1。
- **`sorted(a)` 交回一串新的、排好的 list，a 不動；`a.sort()` 直接把 a 本身排好，交回 `None`（什麼都沒有）。** 所以 `b = a.sort()` 拿到的 b 是 `None`。append、insert、remove 也一樣，只改 list、交回 `None`。不確定拿到什麼，就先印出來看。
- 要留著原本的順序，就用 `sorted`。
- 第③圈：assert 也可以比整串 list：`assert a == [120, 85]` 是在問 a 現在是不是這兩筆、而且是這個順序。要檢查「呼叫完以後 list 變成什麼樣子」，先把 list 放進一個名字（例如 `b = [120, 300, 85]`），呼叫完再比 b。只看交回的答案，抓不到「答案對、可是多做了一件事」的版本。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-13
```

它會把起點檔複製到你的帳本 `lessons/1-13/`：`index.txt`、`ledger.py`、`fix.py`、`sort.py`、`sort_quiz.txt`、`tutor.md`、`entries.py`（課程版本，不用改）、`checks_list.py`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-13/ledger.py
uv run lessons/1-13/fix.py
uv run lessons/1-13/sort.py
uv run lessons/1-13/checks_list.py
```

`checks_list.py` 跑起來什麼都沒印，代表每一條 assert 在正確版上都成立。檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-13
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-13`。）

## 4. 成品示範

```
$ uv run lessons/1-13/ledger.py
一共 5 筆，合計 650 元
第一筆 120 元，最後一筆 150 元
$ uv run lessons/1-13/fix.py
95
[120, 60, 200]
$ uv run lessons/1-13/sort.py
由小到大 [85, 95, 120, 200]
原本的順序 [120, 85, 200, 95]
```

第③圈只檢查了交回的答案時，check 會說：

```
你的檢查抓到 2 個壞版本，還有 1 個溜過去：
  ・查完最大的以後，原本的 list 還是原本的順序嗎？
```

## 5. 怎麼測

`uv run check.py 1-13` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。一共 17 題：

- 第一圈：`index.txt` 4 題、`ledger.py` 2 題（原本的 amounts 跑一次；check 把 amounts 換成別的三筆再跑一次）、`fix.py` 1 題、`sort.py` 2 題（一樣跑兩次）
- 第二圈：`sort_quiz.txt` 3 題
- 第三圈：至少寫 5 條 assert、在正確版上全部成立、抓到 3 個壞版本。寫滿 5 條以前，只告訴你抓到幾個，不告訴你溜過去的是哪一種

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。`tutor.md` 是自評，check 不檢查。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| 第一筆印出 85 | 索引從 1 開始數了 | 第一筆是 `amounts[0]` |
| `IndexError: list index out of range` | 索引超出範圍（四筆最大的索引是 3） | 最後一筆用 `amounts[-1]` |
| `ValueError: list.remove(x): x not in list` | remove 括號裡的值不在 list 裡（多半是寫成了索引） | remove 括號裡寫金額，例如 `remove(85)` |
| sort.py 兩行一模一樣，都是排好的 | 用了 `amounts.sort()`，原本的順序被改掉了 | 改用 `sorted(amounts)` |
| 印出 `None` | 把 `a.sort()` 或 `a.append(…)` 交回的東西拿去用了 | 要排好的一串新的用 `sorted(a)`；append 完直接印 `a` |
| `ModuleNotFoundError: No module named 'entries'` | 自己試跑時，`entries.py` 不在同一個資料夾 | 在課程資料夾打 `uv run check.py start 1-13`，它會把 `entries.py` 複製過去 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-13 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、Python 官方文件的原文、insert 的索引超過長度會怎樣、第③圈三個壞版本各錯在哪）在 `補充.md`。
