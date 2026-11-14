# 1-8　比較、邏輯與 assert

這課大約 45 分鐘。三圈比例 70／20／10。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：`print`、變數（1-2）、資料型別 `bool`（1-3）、`input()` 和 `int()`（1-6）、錯誤訊息從最下面看（1-7）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 填真值表（`truth.txt`）：4 題。熊的提醒規則是 `remind = over and not weekend`（超過預算，而且不是週末，才提醒），四種組合各寫 `True` 或 `False`。先不要跑。

B. 超過預算了嗎（`over.py`）：用 `input()` 問這週花了多少、預算多少，印出「超過預算了嗎？」和一個比較的結果。剛好花到預算**不算**超過。

C. 是週末嗎（`weekend.py`）：用 `input()` 問今天星期幾（打一個字，例如「六」），印出「是週末嗎？」和結果。星期六或星期日都算週末。

**第②圈：用自己的例子，驗證家教說得對不對。**

A. `ai_check.txt`（對答 3 題）：影片裡熊問家教，為什麼 `budget > 0 and spent / budget > 0.8` 在預算是 0 的時候沒有當掉。照家教對「短路求值」的說法猜，再自己跑跑看。

B. `my_test.md`（自評）：問家教一個 and 或 or 的問題，挑它的一句話，自己寫兩三行程式驗證。影片裡熊跟家教的完整對話在 `補充.md`。

**第③圈：用 assert 替 AI 寫的 `over_budget()` 驗收（`checks_budget.py`）。** 需求卡：

| 欄 | 內容 |
|---|---|
| 目標 | 寫一個 `over_budget(spent, budget)`，告訴記帳程式「超過預算了嗎」 |
| 背景 | 花超過預算的時候要提醒；常常有人剛好花到預算 |
| 限制 | 花的比預算多，才算超過；**剛好花到預算，不算超過**；交回 `True` 或 `False` |
| 怎樣算做完 | 你寫的 assert（至少 5 條）在正確版上全部成立；三個壞版本，各被至少一條抓到 |

AI 照這張需求卡寫了 `over_budget()`（課程凍結的版本：正確版在 `reference/`，三個壞版本在 `mutants/`）。你**不用看懂它的程式**，也先不要看，只要在 `checks_budget.py` 裡**呼叫**它，把一定要成立的事寫成 assert：

```python
from budget import over_budget

assert over_budget(1200, 1000) == True
```

`uv run check.py 1-8` 會把你的 `checks_budget.py` 拿去跑正確版和三個壞版本（每個版本各跑一次、互不影響），正確版上要全部成立，每個壞版本至少要有一條不成立。

## 2. 提示

- 這一課先認識六種比較（官方文件另外還有 `is`、`is not`，之後才會用到）：`>` 大於、`<` 小於、`>=` 大於或等於、`<=` 小於或等於、`==` 一樣嗎、`!=` 不一樣嗎。比較的結果一定是 `True` 或 `False`（1-3 的 bool）。
- **一個等號是「放進去」，兩個等號是「問一不一樣」。** `budget = 1000` 是把 1000 放進 budget；`spent == budget` 是在問兩個一不一樣。在 assert 裡比較，一定是兩個等號。
- 加了引號的 `"1000"` 是字串，跟整數 `1000` 永遠不一樣：`"1000" == 1000` 是 `False`。`input()` 交回來的是字串，要先用 `int()` 轉成整數再比。
- `and`：兩邊都成立才成立；`or`：有一邊成立就成立；`not`：反過來。一起用的時候，`not` 先算，再算 `and`，最後算 `or`；不確定就加括號。
- 判斷 day 是不是「六」或「日」這種寫法，`or` 的兩邊要各寫一個完整的比較：`day == "六" or day == "日"`。寫成 `day == "六" or "日"` 不會出錯，可是右邊的「日」是有字的字串，Python 會把它當成真（真假值），結果就不對了。
- 真假值：`0`、空字串 `""`、`None` 會被當成假；有字的字串（連 `"0"`、`" "` 都算）當成真。
- 短路求值：`and` 的左邊是假，整個一定是假，右邊不會算；`or` 的左邊是真，整個一定是真，右邊不會算。所以 `budget > 0 and spent / budget > 0.8` 要把 `budget > 0` 寫在前面。
- assert 成立的時候**什麼都不會印**；不成立會跳出 `AssertionError`，最後一行往上看，是第幾行那一條。
- 第③圈最容易漏的，是「剛好等於」的那一種：需求卡已經寫了它算哪一邊。比預算多一點點、少一點點的，也值得各寫一條。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-8
```

它會把起點檔複製到你的帳本 `lessons/1-8/`：`truth.txt`、`over.py`、`weekend.py`、`ai_check.txt`、`my_test.md`、`budget.py`（課程版本，不用改）、`checks_budget.py`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-8/over.py
uv run lessons/1-8/weekend.py
uv run lessons/1-8/checks_budget.py
```

`checks_budget.py` 跑起來什麼都沒印，代表每一條 assert 在正確版上都成立。檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-8
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-8`。課號寫 `1-08` 也可以。）

## 4. 成品示範

```
$ uv run lessons/1-8/over.py
這週花了多少？1200
預算是多少？1000
超過預算了嗎？ True
```

還沒抓到所有壞版本的時候，check 會說：

```
你的檢查抓到 2 個壞版本，還有 1 個溜過去：
  ・剛好花到預算（花 1000、預算 1000 算超過嗎？）
```

全部做完的時候：

```
你的檢查把 3 個壞版本全部抓到了。
```

## 5. 怎麼測

`uv run check.py 1-8` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。一共 17 題：

- 第一圈：`truth.txt` 4 題、`over.py` 2 題（check 自己餵兩組：1200 和 1000、1000 和 1000）、`weekend.py` 3 題（六、日、三）
- 第二圈：`ai_check.txt` 3 題
- 第三圈：至少寫 5 條 assert、在正確版上全部成立、抓到 3 個壞版本。寫滿 5 條以前，只告訴你抓到幾個，不告訴你溜過去的是哪一種

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。`my_test.md` 是自評，check 不檢查。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡（多半是剛剛在帳本試跑完忘了切回來） | 先打 `cd ~/code/plusform-course`，或用完整路徑 `uv run ~/code/plusform-course/check.py 1-8` |
| `比較兩個東西一不一樣，要用兩個等號 ==` | assert 裡寫成一個等號（`SyntaxError`） | `assert over_budget(1000, 1000) == False` |
| `True、False 第一個字母要大寫` | 寫成了 `true`、`false` | 改成 `True`、`False`，不加引號 |
| `ModuleNotFoundError: No module named 'budget'` | 自己試跑時，`budget.py` 不在同一個資料夾 | 在課程資料夾打 `uv run check.py start 1-8`，它會把 `budget.py` 複製過去 |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-8 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡家教回答的逐字紀錄、Python 官方文件的原文、`and`／`or` 交回的其實是其中一邊的值、`python -O` 會略過 assert）在 `補充.md`。
