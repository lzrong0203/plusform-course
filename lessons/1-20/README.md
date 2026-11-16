# 1-20　看懂 AI 常用的寫法（下）：型別提示、lambda、sorted 的 key、any／all、*args

這課大約 55 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：推導式（1-17）、def、參數、return、呼叫時的小框、docstring（1-18）、關鍵字參數（1-19）、dict 的 `get`、`items`（1-15）、tuple 拆包（1-14）、`sorted`、切片（1-13）、assert（1-8）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 先猜（`predict.txt`）：3 題，先不要跑，用眼睛追。

B. 把 AI 的一行改回普通寫法（`plain.py`）。上面是 AI 寫的 5 行（有 `lambda`、`any`、`all`），下面改寫成不用 lambda、不用 any／all 的版本：有 lambda 的，先用 `def` 寫一個函式（例如 `amount_of`），key 交那個函式的名字；`any`／`all` 改回 for 迴圈。第一行已經改好當範例。每改好一個，下面寫一條 `assert` 確認跟 AI 寫的一樣。最後一行 print 不要改，五個都一樣就印出 `True True True True True`。

C. 依金額、再依日期排序（`sort2.py`）。金額由小到大；金額一樣的，再依日期由早到晚。

**第②圈：請家教考你 key 每次收到的是什麼（`tutor.md`）。** 在家教專案裡貼上 AI 寫的排序（`tutor.md` 有那兩行），請它出一題考你 key 的部分、先不要解釋。先用自己的話回答；家教說不對的地方，把 lambda 改回 def、在函式裡加一行 print，自己跑一次確定。記在 `tutor.md`（四個標籤都寫了就算交了，內容不改對錯）。再做白話翻譯 4 題（`translate.txt`）。

**第③圈：型別提示、docstring、assert 交出去，用測試驗收。** 要一個函式「依分類排出前三大花費」。跟 1-18 一樣先寫好要交出去的東西：

1. 函式的名字和型別提示（`top3.py` 已經寫好 `def top3(entries: list[tuple[str, int]]) -> list[tuple[str, int]]:`）
2. docstring：寫清楚**輸入**、**輸出**（合計大的在前、最多三類、空的交回 `[]`）、**例子**（例子寫一次真的呼叫和它交回的值）
3. assert：在 `checks_top3.py` 至少寫 3 條

把 def 那一行、docstring 和 assert 一起貼給 AI（免費的聊天版就可以），請它照 docstring 寫函式內容、assert 不要改，再把它寫的函式內容貼進 `top3.py`。**沒有 AI 帳號的**，打開課程資料夾的 `lessons/1-20/frozen/top3.py`（課程的凍結版，影片裡 AI 寫的那一份），把 docstring 下面的函式內容抄過來。課程另外藏了 3 個 AI 寫錯的版本（範例示意），你的 assert 要每一個都抓到；其中一個是 **排序方向寫反**（合計從小排到大）。

**選做加深（check 不檢查）：遞迴（`deep.py`）。** 函式裡呼叫自己。只要追得出巢狀清單的加總就好：先用眼睛追最下面那一行會印出什麼，再跑一次對答案。一步一步的追法在 `補充.md`。

## 2. 提示

- **型別提示：** `def double(amount: int) -> int:` 的 `: int` 是「amount 應該交一個整數」，`-> int` 是「會交回一個整數」。它是寫給人和工具（例如 VS Code）看的說明，**Python 跑的時候不檢查**：`double("120")` 照樣跑，印出 `120120`（字串乘以二＝接兩次），不會出現錯誤訊息。真的要確定，交進去跑跑看、用 assert 檢查。`list[tuple[str, int]]` 讀成「一個 list，裡面每一筆是（字串, 整數）的 tuple」。
- **sorted 的 key：** `sorted(entries, key=amount_of)`：排之前，先把**每一筆**各交給 `amount_of` 一次，照它交回的值來比。key 收到的是一筆，不是整個 list，也不是編號。sorted 做出一個新的 list，原本的不變。
- **lambda：** `lambda e: e[1]` 是一個沒有名字的小函式：冒號前面的 `e` 是參數，冒號後面是交回的值。改回普通寫法：`def amount_of(e):` 下一行 `return e[1]`，key 交 `amount_of`。官方教學：lambda 只能寫一個運算式，就是一般函式的簡寫。
- **reverse 與穩定排序：** `reverse=True` 從大排到小。key 一樣大的，sorted 會照原本的順序放（穩定排序，官方保證；reverse=True 也一樣）。要「先依金額、再依日期」，就排兩次：先照日期排，再照金額排。
- **any、all：** `any(a >= 300 for a in amounts)` 是「有沒有任何一筆 >= 300」，`all(...)` 是「是不是每一筆都…」，交回 True 或 False。括號裡跟推導式一樣讀，只是少了方括號。改回迴圈：any 先給 False、遇到符合的改 True；all 先給 True、遇到不符合的改 False。空的時候 `any([])` 是 False、`all([])` 是 True。
- **\*args、\*\*kwargs：** `def total(*amounts):` 交幾個都可以，全部包成一個 tuple 叫 amounts（`total(120, 85, 300)` 的 amounts 是 `(120, 85, 300)`）。`def show(**opts):` 用名字交的參數包成一個 dict（`show(month=11, budget=1000)` 的 opts 是 `{'month': 11, 'budget': 1000}`）。
- 第③圈的 assert：只有一類，排得對不對看不出來。放兩類以上、同一類好幾筆、金額有大有小、分類多於三類，才抓得到排反了、沒加總、沒只留前三類。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-20
```

它會把起點檔複製到你的帳本 `lessons/1-20/`：`predict.txt`、`plain.py`、`sort2.py`、`translate.txt`、`tutor.md`、`top3.py`、`checks_top3.py`、`deep.py`（選做），還有影片裡熊的示範檔 `sort.py`（跟著打，不檢查）。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-20/plain.py
uv run lessons/1-20/sort2.py
uv run lessons/1-20/checks_top3.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-20
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-20`。）

## 4. 成品示範

```
$ uv run lessons/1-20/plain.py
True True True True True
$ uv run lessons/1-20/sort2.py
11/01 車 85
11/04 餐 85
11/02 書 120
11/03 餐 120
$ uv run lessons/1-20/checks_top3.py
$
```

`checks_top3.py` 什麼都沒印出來，代表每一條 assert 都成立。

## 5. 怎麼測

`uv run check.py 1-20` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。第一圈：`predict.txt` 3 題、`plain.py`（五個都跟 AI 寫的一樣、key 交的是 def 寫的函式、any／all 改回迴圈；entries 換掉再跑一次）、`sort2.py`（兩組資料）；第二圈：`translate.txt` 4 題、`tutor.md` 四個標籤寫了沒；第三圈：`top3.py` 的型別提示、docstring 和 return、直接呼叫 top3 三次、你的 assert 抓不抓得到 3 個 AI 寫錯的版本、你的 assert 在你的 top3.py 上全部成立。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `NameError: name 'newest2' is not defined` | 還沒改寫 newest2（最後一行 print 要用到它） | 照範例寫 `def date_of(e):`、`newest2 = sorted(entries, key=date_of, reverse=True)` |
| 「newest2 要用 sorted 排，key 交一個用 def 寫的函式」 | 你還是用了 lambda，或直接寫 `newest2 = newest` | 先 `def` 一個函式，key 交它的名字 |
| plain.py 印出 `True False True True True` | 第二個跟 AI 寫的不一樣 | 看 `reverse=True` 有沒有一起寫 |
| sort2.py 只照日期排好 | 兩次的順序反了（先金額、再日期） | 先照日期排，再照金額排 |
| 「top3(…) 應該回傳 [('書', 450), ('餐', 420), ('衣', 60)]」，交回的是從小排到大 | 排序方向寫反 | `reverse=True` |
| 第三圈「壞版本 1 沒抓到」 | 你的 assert 都只有一類 | 再寫一條兩類以上、合計不一樣的 |
| 「top3 的型別提示還沒寫完」 | def 那一行的 `: …`、`-> …` 被刪掉了 | 照起點檔留著 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-20 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教、聊天版 AI 的完整對話、Python 官方文件的原文、選做的遞迴怎麼追）在 `補充.md`。
