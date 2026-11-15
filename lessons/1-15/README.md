# 1-15　dict：用名字找資料

這課大約 50 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：`print`、變數與等號（1-2）、`round`（1-4）、f-string（1-5）、`if`（1-9）、`break`（1-10）、`for`（1-11）、list（1-13）、tuple 與拆包（1-14）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. dict 預測（`predict.txt`）：5 題，先不要跑，用眼睛追。

B. 各分類的小計和筆數（`totals.py`）。`entries` 是這個月的每一筆帳 `(分類, 金額)`。照三步寫：

1. `totals = {}`，用 `for kind, amount in entries:` 拆包，`totals[kind] = totals.get(kind, 0) + amount`
2. `counts = {}`，一樣的寫法，加的是 1：`counts[kind] = counts.get(kind, 0) + 1`
3. 用 `for kind, amount in totals.items():` 一類印一行，例如「餐飲 205 元，2 筆」

C. 預算燈號改成 dict 對照表（`light.py`）。1-9 家教建議「把規則變成資料：放進清單或字典，再用迴圈從頭檢查」，熊那時候還沒學 dict，先不採用；現在採用。預算 1000 元、金額都是整數元：

| 燈號 | 最多花到幾元 |
|---|---|
| 綠燈 | 799（低於 800） |
| 黃燈 | 1000（剛好 1000 也是黃燈） |
| 紅燈 | 超過 1000 |

`limits = {"綠燈": 799, "黃燈": 1000}` 照「從小到大」放。`light` 先放 `"紅燈"`，再用 `for name, top in limits.items():` 從頭比，花的錢 `<= top` 就換成 `name`、`break` 停下來。多一種燈，只要在 `limits` 裡多放一筆。

**第②圈：請家教帶你寫「各分類占了幾 %」（`percent.py`、`lead.md`、`dict_quiz.txt`）。** 這是 0-8、1-10 用過的「帶我寫」：每一步**你先說要做什麼、先寫寫看**，家教才告訴你對不對、給那一步的程式。哪一步說不出來，就知道那一步還不會。家教說你哪裡不對，自己在帳本裡跑一次，確定它說得對不對。寫好的程式放 `percent.py`，過程記在 `lead.md`（自評，不擋過關）。`dict_quiz.txt` 有三題 dict 的工具。

**第③圈：用註解和 assert 寫下需求，驗收 AI 寫的占比小工具（`checks_share.py`、`req_fix.txt`）。** 需求卡：

| 欄 | 內容 |
|---|---|
| 目標 | 算出各分類占了幾 %：`shares(totals)` |
| 背景 | `totals` 是各分類的小計（dict：分類 → 金額） |
| 限制 | 1. 每一類＝小計 ÷ 全部 × 100，用 `round` 留到小數一位　2. 每個分類都要有（花 0 元的是 0.0）　3. 不能動到原本的 `totals`　4. 各分類的占比加總要顯示 100% |
| 怎樣算做完 | 用註解寫下要求、用 assert 寫下一定要成立的事（至少 3 條），在正確版上全部成立，三個壞版本各被至少一條抓到 |

AI 照這張需求卡寫了 `share.py`（課程凍結的版本：正確版在 `reference/`，三個壞版本在 `mutants/`）。你**不用看懂它的程式**（`def` 到 1-18 才教），只要在 `checks_share.py` 裡**呼叫**它：

```python
from share import shares

# 每一類＝小計 ÷ 全部 × 100，留到小數一位
t = {"餐飲": 160, "交通": 100, "娛樂": 40}
r = shares(t)
assert r == {"餐飲": 53.3, "交通": 33.3, "娛樂": 13.3}
```

需求卡第 4 條也要寫成 assert 跑跑看。**它在正確版上不成立時，先判斷是誰的問題**：程式寫錯了？你的 assert 寫錯了？還是需求本身沒講清楚？需求沒講清楚，就在那一行最後加上 `# 需求有問題`，再打開 `req_fix.txt`：判斷是誰的問題、照影片裡熊採用的規則替需求卡補一條（少掉的那一點點要歸給哪一類）、照這條規則算一次。

`uv run check.py 1-15` 會把你的 `checks_share.py` 拿去跑正確版和三個壞版本（每個版本各跑一次、互不影響），正確版上要全部成立（標了「# 需求有問題」的那一行另外判），每個壞版本至少要有一條不成立。

## 2. 提示

- **dict** 是一張對照表：大括號裡一組一組的 `鍵: 值`，用逗號隔開。`totals = {"餐飲": 205, "交通": 75}`。冒號左邊叫**鍵**（名字），右邊叫**值**。
- **用名字找**：`totals["餐飲"]` 是 205。不用數第幾個（list 和 tuple 用索引，dict 用鍵）。
- **新增或換掉**：`totals["娛樂"] = 200`，沒有這個鍵就多一組（加在最後面）；已經有的鍵再放一次，是把值換掉（鍵不會重複）。
- `len(totals)` 是有幾組；`"交通" in totals` 問的是**鍵**在不在。
- **查不到的鍵**：`totals["醫療"]` 會出現 `KeyError: '醫療'`（找不到這個鍵），不會變成 0。要查不到時有預設值，用 `totals.get("醫療", 0)`：查得到交回值，查不到交回 0。只寫 `totals.get("醫療")` 查不到交回 `None`。`get` 只是查，不會把鍵放進去。
- **計數**：一開始是空的 `{}`（空的大括號是 dict；1-14 的空 set 要寫 `set()`）。`totals[kind] = totals.get(kind, 0) + amount`：第一次遇到的分類，get 交回 0。加的是 1 就是數幾筆。
- **dict 記得放進去的順序**（Python 3.7 起的保證）：印出來、`for` 拿出來，都照放進去的先後；換掉某個鍵的值，位置不變。1-14 的 set 沒有保證順序。
- **for 和 dict**：`for k in totals:` 拿到的是**鍵**。`totals.values()` 是所有的值、`totals.keys()` 是所有的鍵、`totals.items()` 一圈給一組 `(鍵, 值)`：`for kind, amount in totals.items():`。
- `sum(totals)` 加的是鍵（文字），會出現 `TypeError`；全部加起來要寫 `sum(totals.values())`。
- **list 裡放 dict**：`entries = [{"item": "午餐", "amount": 120}, {"item": "公車", "amount": 30}]`。先用索引拿第幾筆（`entries[1]`），再用鍵拿那一樣（`entries[1]["item"]` 是公車）。
- 兩個 dict 用 `==` 比：每一組鍵和值都一樣就相等，順序不用一樣。
- `round(x, 1)` 留到小數一位。剛好一半的時候不是四捨五入，是選偶數那邊（`round(2.5)` 是 2、`round(3.5)` 是 4），小數本身也存不準（`round(2.675, 2)` 是 2.67）；細節在 `補充.md`。
- 小數加起來會有一點點誤差（1-3 的 0.1 + 0.2）：`33.3 + 33.3 + 33.3` 是 `99.89999999999999`。比加總要先 `round(…, 1)`。
- 第③圈：check 說某一條在正確版上不成立，**不一定是程式錯**。先對一次需求卡：程式有照需求做嗎？你的 assert 有照需求寫嗎？兩個都對，卻還是做不到，就是需求本身沒定規則，要回頭補規則（不是自己猜一個答案改程式）。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-15
```

它會把起點檔複製到你的帳本 `lessons/1-15/`：`predict.txt`、`totals.py`、`light.py`、`percent.py`、`dict_quiz.txt`、`lead.md`、`share.py`（課程版本，不用改）、`checks_share.py`、`req_fix.txt`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-15/totals.py
uv run lessons/1-15/light.py
uv run lessons/1-15/percent.py
uv run lessons/1-15/checks_share.py
```

`checks_share.py` 跑起來什麼都沒印，代表每一條 assert 在正確版上都成立；出現 `AssertionError`，看錯誤訊息說的是第幾行。檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-15
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-15`。）

## 4. 成品示範

```
$ uv run lessons/1-15/totals.py
餐飲 205 元，2 筆
交通 75 元，2 筆
娛樂 200 元，1 筆
$ uv run lessons/1-15/light.py
這個月花了多少？1000
黃燈
$ uv run lessons/1-15/percent.py
餐飲 42.7 %
交通 15.6 %
娛樂 41.7 %
```

第③圈把需求卡第 4 條寫成 assert、還沒標的時候，check 會說：

```
第 N 行：assert round(sum(r.values()), 1) == 100
  在正確版上就不成立（正確版算出來是99.9）。
  正確版不會錯，所以是這條檢查要改；如果你覺得是需求沒講清楚，在行尾加上「# 需求有問題」。
```

## 5. 怎麼測

`uv run check.py 1-15` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。一共 23 題：

- 第一圈：`predict.txt` 5 題、`totals.py` 2 題（原本的 entries 跑一次；check 把 entries 換成別的幾筆再跑一次）、`light.py` 2 題（餵 500、800、1000、1001 各跑一次；再在 limits 裡多加一燈橘燈跑一次）
- 第二圈：`percent.py` 2 題（一樣跑兩次）、`dict_quiz.txt` 3 題
- 第三圈：至少寫 3 條 assert、在正確版上全部成立、抓到 3 個壞版本、至少一行標「需求有問題」（判對了才算）；`req_fix.txt` 3 題。寫滿 3 條以前，只告訴你抓到幾個，不告訴你溜過去的是哪一種

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。`lead.md` 是自評，check 不檢查。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `KeyError: '醫療'` | 用方括號拿一個 dict 裡沒有的鍵 | 先用 `in` 問有沒有，或用 `get("醫療", 0)` |
| totals.py 第一圈就 `KeyError: '餐飲'` | `totals[kind] + amount`：空的 dict 裡還沒有這個鍵 | 改成 `totals.get(kind, 0) + amount` |
| `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | `sum(totals)` 加的是鍵（文字） | 寫 `sum(totals.values())` |
| 印出「餐 飲」「交 通」，或 `ValueError: too many values to unpack` | `for kind, amount in totals:` 拿到的只有鍵：兩個字的鍵被拆成兩個字，三個字的就拆不完 | 寫 `for kind, amount in totals.items():` |
| light.py 花 1000 印出紅燈 | 寫成 `spent < top`，剛好 1000 不算黃燈 | 黃燈是「最多 1000 元」：`spent <= top` |
| light.py 第二題「找不到 limits = {...} 這一行」 | 燈號寫死在 if／elif 裡 | 留著 limits 那一行，用 for 照 limits 一個一個比 |
| 第③圈「這條在正確版上不成立」，加總是 99.9 | 需求卡第 4 條 | 先判斷是誰的問題（見第 2 節最後一點），需求沒定規則就標 `# 需求有問題`、到 `req_fix.txt` 補規則 |
| `ModuleNotFoundError: No module named 'share'` | 自己試跑時，`share.py` 不在同一個資料夾 | 在課程資料夾打 `uv run check.py start 1-15`，它會把 `share.py` 複製過去 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-15 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、Python 官方文件的原文、round 剛好一半時怎麼算、加總為什麼是 99.9、第③圈三個壞版本各錯在哪）在 `補充.md`。
