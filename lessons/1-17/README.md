# 1-17　看懂 AI 最愛的寫法（上）：推導式、zip

這課大約 45 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：if（1-9）、for 與 enumerate（1-11）、list 的 `append`、`len`、`sum`（1-13）、tuple 拆包（1-14）、assert（1-8）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 先猜（`predict.txt`）：3 題，先不要跑，用眼睛追。

B. 迴圈和推導式互相改寫（`convert.py`）。上面三段是迴圈，在每一段下面把 `cut2`、`big2`、`use2` 改成一行推導式；最後一段反過來，把推導式 `small` 改回迴圈（`small2 = []` 留著，下面寫 for、if、append）。每一段都有一條 `assert`，確認兩種寫法的結果一樣。`amounts` 那一行和最後四行 `print` 不要改。

C. 用 zip 配對（`pairs.py`）。上面兩行是日期和金額（一天一筆），在下面先用 `assert` 確認兩串一樣長，再用 `for` 和 `zip` 一天印一行，例如 `11/01 120 元`。

**第②圈：請家教把你的迴圈改精簡，逐行用白話解釋（`tutor.md`、`short_quiz.txt`）。** 在家教專案裡貼一段你寫的迴圈（`tutor.md` 有一段範例），請它改精簡、只用學過的東西、逐行用白話解釋。**每一行你都要能用自己的話解釋，解釋不出來的就不收。** 家教說你解釋錯了，自己跑一次確定；最後用同一條 assert 確認精簡版跟原本的迴圈結果一樣。記在 `tutor.md`（自評，不擋過關）。`short_quiz.txt` 有四題。

**第③圈：白話描述題（兩條選一條）。**

- **有 AI 帳號的（免費的聊天版就可以）：** 先讀懂 `report.py`（課程準備的報表程式，範例示意），在 `describe.md` 用白話描述它在做什麼，寫到別人沒看過程式、照著做也會印出一模一樣的字。把描述整段貼給聊天版 AI，請它寫 Python 程式，再把程式貼進 `answer.py` 最下面（上面兩行資料不要改；AI 的程式裡如果又寫了一次 `dates`、`amounts`，把那兩行刪掉）。check **只跑測試**：用原本的資料、一組有剛好 100 元的資料、一組沒有 100 元以上的資料各跑一次，印出來要跟 `report.py` 一樣（空格多少不算）。把 `report.py` 直接抄進去也會過，可是這一圈練的是「描述寫到 AI 照做就對」，抄了就沒練到。
- **沒有 AI 帳號的：** 做 `describe_quiz.txt`，三題「哪一段白話描述對得上這段程式」。

兩條做一條就好；兩條都做了，check 照全過的那一條判。

## 2. 提示

- **推導式＝把「先做空的 list，再一筆一筆 append」的迴圈折成一行。** `[a - 20 for a in amounts]` 跟下面這段做的是同一件事，做出一個新的 list，`amounts` 本身不會變：

  ```python
  cut = []
  for a in amounts:
      cut.append(a - 20)
  ```

- **讀的順序：先看中間的 for，再看後面的 if，最後看最前面。** `[a - 20 for a in amounts if a >= 100]` 用白話說：從 amounts 一筆一筆拿出 a，100 以上的（100 也算），放 a 減 20 進去。
- **改回迴圈：for、if 照順序抄成兩行，最前面那一段變成最裡面的 append。** 官方教學：the order of the for and if statements is the same（兩種寫法裡 for 和 if 的順序一樣）。改完用同一條 `assert 迴圈的結果 == 推導式的結果` 確認一樣。
- 最前面寫 `a >= 100` 不是篩選，會得到一串 True／False；要篩選，`if` 寫在 `for` 後面。
- **zip 把兩串一格一格配成一對一對**（每一對是一個 tuple），`for d, a in zip(dates, amounts):` 用 1-14 的拆包一次拿出日期和金額。`d` 是日期本身，不是編號。
- **zip 長度不同時，停在比較短的那一串**，多出來的不會出錯誤訊息（官方文件：By default, zip() stops when the shortest iterable is exhausted），少記一筆很難發現。配對之前先 `assert len(dates) == len(amounts)`；Python 3.10 起也可以寫 `zip(dates, amounts, strict=True)`，長度不同就丟 `ValueError`。
- **enumerate 也是配成一對對**：（編號, 值）。`enumerate(amounts, start=1)` 編號從 1 開始，值還是從第一筆開始；沒寫 start 從 0 開始。
- 第③圈的描述要寫清楚：資料放在哪兩個名字、哪幾筆要印（**100 算不算**）、一行印什麼、最後一行印什麼。少一句，AI 就可能寫成另一支程式（例如 `> 100`），check 換成剛好 100 元的資料就抓得到。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-17
```

它會把起點檔複製到你的帳本 `lessons/1-17/`：`predict.txt`、`convert.py`、`pairs.py`、`short_quiz.txt`、`tutor.md`、`report.py`、`describe.md`、`answer.py`、`describe_quiz.txt`，還有影片裡熊打的示範檔 `same.py`（check 不檢查，想跟著影片打一次就用它）。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-17/convert.py
uv run lessons/1-17/pairs.py
uv run lessons/1-17/report.py
uv run lessons/1-17/answer.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-17
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-17`。）

## 4. 成品示範

```
$ uv run lessons/1-17/convert.py
[100, 65, 280, 25]
[120, 300]
[100, 280]
[85, 45]
$ uv run lessons/1-17/pairs.py
11/01 120 元
11/02 85 元
11/03 300 元
11/04 45 元
$ uv run lessons/1-17/answer.py
11/01 120 元
11/03 300 元
100 元以上的有 2 筆，合計 420 元
```

## 5. 怎麼測

`uv run check.py 1-17` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。一共 14 題：

- 第一圈：`predict.txt` 3 題、`convert.py` 2 題（原本的跑一次，要真的是推導式和迴圈；check 把 amounts 換掉再跑一次）、`pairs.py` 2 題（一樣跑兩次，第二次換三天的資料）
- 第二圈：`short_quiz.txt` 4 題
- 第三圈：3 題。AI 版：`answer.py` 換三組資料各跑一次；選擇題版：`describe_quiz.txt` 3 題。照你做的那一條判

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。`tutor.md`、`describe.md` check 不檢查。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `AssertionError`（convert.py） | 那一段的推導式和迴圈，結果不一樣 | 照「先看 for、再看 if、最後看最前面」再翻一次白話，跟迴圈一行一行對 |
| 「cut2 要用一行推導式寫」 | 寫成 `cut2 = cut` 或直接寫答案 | 改成 `cut2 = [a - 20 for a in amounts]` 這種一行的寫法 |
| 「要改回迴圈」 | small2 不是用 for 迴圈 append 出來的 | `small2 = []` 留著，下面寫 `for a in amounts:`、`if a < 100:`、`small2.append(a)` |
| convert.py 第二題沒過，第一題過了 | 用 `>` 寫成「100 不算」，換掉的金額裡有剛好 100 | 題目要 100 元以上（100 也算），用 `>=` |
| pairs.py 只印三行 | 日期和金額長度不一樣，zip 停在比較短的那一串 | 檢查兩串，先 `assert len(dates) == len(amounts)` |
| 第三圈第 2 題沒過 | AI 寫成 `> 100`（描述沒寫 100 也算），或 AI 又寫了一次 dates、amounts | 描述補一句「100 也算」再請 AI 寫一次；把 AI 自己寫的資料那兩行刪掉 |
| 第三圈全部沒過、說「兩條選一條做」 | answer.py 還沒貼程式，describe_quiz.txt 也還沒作答 | 選一條做 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-17 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教、聊天版 AI 的完整對話、Python 官方文件的原文、推導式裡的名字跑完不會留在外面、`strict=True`、選擇題版的讀法提示）在 `補充.md`。
