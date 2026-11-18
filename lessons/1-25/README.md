# 1-25　Debugger 與編輯器導覽

這課大約 45 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打；這課的 F 鍵（F5、F9、F10、F11、F12）Mac 和 Windows 一樣，只有「尋找所有參考」兩邊按法不同（第 2 節的表）。
要會的：模組與 import（1-21）、讀 Traceback（1-22）、`date(年, 月, 日)` 和 `d.year`、`d.month` 這種屬性（1-21、1-24）、assert（1-8）。

## 1. 題目

熊的月報程式 `report.py` 會印出這期和下期的扣款日。它用到旁邊三個檔：`settings.py`（每個月幾號扣款）、`card.py`（信用卡）、`dates.py`（加一個月）。跑起來印出第一行就當掉：

```
這期扣款 2026-01-31
Traceback (most recent call last):
  …
ValueError: day is out of range for month
```

**第①圈：用 debugger 和編輯器導覽找原因（關掉 AI）。** 照影片做一次，再寫 `debug.txt` 4 題：

A. 在 `report.py` 第 7 行的行號左邊點一下（或按 F9），出現紅點＝中斷點。編輯區開著 `report.py`，按 F5 開始 debug（第一次會問要用什麼，選 Python Debugger，再選 Python File）。

B. 程式停在第 7 行：亮起來的那一行是「下一個要跑的」。看左邊的 VARIABLES（變數面板），再按 F10（Step Over）跑完這一行，看多出了什麼。

C. 停在第 9 行時按 F11（Step Into），走進 `dates.py` 的 `next_month`。看 CALL STACK（呼叫堆疊）：最上面是現在在哪裡，下面是誰呼叫它的。再按 F10，看它在哪一行、為什麼停下來。

D. `settings.py` 寫的是 15，d 為什麼是 31 號？在 `report.py` 第 7 行的 `PAY_DAY` 上按 F12（Go to Definition，移至定義），再按右鍵選 Find All References（尋找所有參考），找出哪一個檔的哪一行把它改掉了。

**第②圈：只指著一行問家教。** 規則：只能指著某一行問「這一行在做什麼？」，不貼整支程式、不請它修。照 `tutor.md` 的步驟問，它說的用 debugger 停在那一行對照，記在 `tutor.md`（三個標籤都寫了就算交了，內容不改對錯）。再做 `ask.txt` 3 題。

**第③圈：寫 bug 回報，再用它驗收課程的修正版。**

A. 用 Markdown 寫 `bug_report.md`（第 2 節有三個符號就夠用）：

- `## 重現步驟`：一行一步、開頭寫 `1.` `2.`，別人照做就看得到同一個錯（在哪個資料夾、打什麼指令）。
- `## 預期`：應該印出什麼。這課的預期是：2 月沒有 31 號，就用 2 月的最後一天，**下期扣款 2026-02-28**。
- `## 實際`：現在發生什麼。錯誤訊息的最後一行，前後各一行三個反引號 ```` ``` ```` 包起來。

寫完用最下面的自評表打勾。

B. 課程的修正版在 `dates_fixed.py`（不要改它）。`report.py` 第 4 行改成 `from dates_fixed import next_month`，**照你寫的重現步驟再跑一次**：要印出你寫的預期。

C. 把重現步驟寫成檢查（`checks_dates.py`），至少 3 條，每一條寫成：

```python
assert next_month(date(2026, 1, 31)) == date(2026, 2, 28)
```

修好一個 bug，要試三種日子：**回報裡的那一天**、**原本就好好的日子**、**年底（12 月加一個月是明年 1 月）**。課程另外藏了 3 個 AI 修錯的版本（範例示意）。你的檢查要在修正版上全部成立（什麼都沒印），在每個修錯的版本上至少有一條不成立。

## 2. 提示

- **debugger：** 讓程式停在你指定的那一行、一步一步跑，邊跑邊看每個變數現在是多少。前面幾課 trace 卡上的箭頭和變數表，就是 debugger 在做的事。
- **按鍵（VS Code 官方文件的預設）：**

| 要做的事 | Mac | Windows |
|---|---|---|
| 設／取消中斷點 | F9（或在行號左邊點一下） | F9（或在行號左邊點一下） |
| 開始 debug／繼續跑到下一個中斷點（Continue） | F5 | F5 |
| Step Over：跑完這一行 | F10 | F10 |
| Step Into：走進這一行呼叫的函式 | F11 | F11 |
| Go to Definition（移至定義） | F12 | F12 |
| Find All References（尋找所有參考） | ⇧⌥F12 | Shift+Alt+F12 |
| Markdown 預覽開在旁邊 | ⌘K 放開再按 V | Ctrl+K 放開再按 V |

  Mac 筆電按 F5 沒有開始 debug，可能是最上面一排被設成亮度、音量這些系統功能：Apple 官方說明是**按住功能（Fn）／地球鍵，同時按下 F5**；也可以在「系統設定」→「鍵盤」→「鍵盤快速鍵」→「功能鍵」選取「使用 F1、F2 等按鍵作為標準功能鍵」。按鍵記不住也沒關係：在名字上按右鍵，選單裡就有 Go to Definition 和 Find All References；debug 的時候，上方的小工具列有 Continue、Step Over、Step Into 的按鈕。
- **亮起來的那一行還沒跑：** VS Code 官方文件：The highlighted execution line is the line that runs next.
- **F10 和 F11：** F10 把這一行整個跑完（裡面呼叫的函式也一起跑完）；F11 走進那個函式，從它的第一行開始一步一步跑。print 這種 Python 內建的，F11 不會走進去。
- **按 F5 跑的是「現在開著的那個檔」：** 編輯區開著 `dates.py` 按 F5，它就去跑 `dates.py`（什麼都不會發生）。先點回 `report.py` 再按。
- **Traceback 和 debugger：** Traceback 告訴你在哪一行當掉；debugger 讓你停在那一行之前，看那一刻每個變數是多少。
- **replace：** `d.replace(month=2)` 做出一個新的日期，只換掉月份，年和日照舊（官方文件：Return a new date object with the same values, but with specified parameters updated.）。1 月 31 日換成 2 月，就是 2 月 31 日，這一天不存在，所以 `ValueError: day is out of range for month`。
- **Markdown：** 用普通符號標出格式的寫法，GitHub、很多筆記軟體都看得懂。這課用三個：一到六個 `#` 開頭是標題（`##` 是第二層，`#` 後面要空一格）；`1.` 開頭是有順序的步驟（點後面一樣空一格）；前後各一行三個反引號，中間包起來的是程式碼或錯誤訊息，照原樣顯示。（GitHub Docs〈Basic writing and formatting syntax〉、CommonMark 規格 0.31.2）
- **為什麼要寫重現步驟：** 修的人照做一次，就看得到同一個錯；修好以後，你再照同樣的步驟跑一次，就知道修好了沒。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-25
```

它會把起點檔複製到你的帳本 `lessons/1-25/`：`report.py`、`settings.py`、`card.py`、`dates.py`、`dates_fixed.py`（課程的修正版，不要改）、`debug.txt`、`tutor.md`、`ask.txt`、`bug_report.md`、`checks_dates.py`。

用 VS Code 打開帳本（這課要用 VS Code 的 Python 擴充，0-6 裝好的那個；右下角的直譯器要是帳本的 `.venv`）。在 VS Code 下面的終端機（帳本資料夾）先跑一次，看它當掉：

```bash
uv run lessons/1-25/report.py
```

第③圈改好以後：

```bash
uv run lessons/1-25/report.py
uv run lessons/1-25/checks_dates.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-25
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-25`。）

## 4. 成品示範

```
$ uv run lessons/1-25/report.py
這期扣款 2026-01-31
下期扣款 2026-02-28
$ uv run lessons/1-25/checks_dates.py
$
```

`checks_dates.py` 什麼都沒印＝每一條都成立。

## 5. 怎麼測

`uv run check.py 1-25` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。第一圈：`debug.txt` 4 題；第二圈：`tutor.md` 三個標籤寫了沒、`ask.txt` 3 題；第三圈：`bug_report.md` 三段都寫了（重現步驟要是編號步驟）、`report.py` 改用修正版以後照重現步驟跑印出預期、你的 `checks_dates.py` 在修正版上全部成立（修正版測試全綠）、抓不抓得到 3 個 AI 修錯的版本。

bug 回報寫得好不好，check 不改對錯：照 `bug_report.md` 最下面的自評表自己打勾。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| 按 F5 什麼都沒發生、或程式沒停 | 編輯區開著的不是 report.py，或沒有紅點 | 點回 report.py；在第 7 行的行號左邊點一下 |
| 紅點是空心的灰色圈 | 那一行沒有可以跑的程式（例如空行、註解） | 點在有程式的那一行 |
| 按 F5 跳出音量或亮度 | Mac 筆電的 F 鍵被設成亮度、音量這些系統功能 | 按住 Fn 再按 F5，或在系統設定改成標準功能鍵 |
| 選單裡沒有 Python Debugger | 還沒裝 Python 擴充 | 照 0-6 裝 Python 擴充（它會一起裝 Python Debugger） |
| `ModuleNotFoundError: No module named 'dates_fixed'` | 第 4 行的名字打錯，或檔案不在 lessons/1-25 | 名字是 dates_fixed（底線）；不要搬動檔案 |
| 下期扣款 2026-02-15 | 把 card.py 的 31 改掉了 | card.py、settings.py 不要改：31 是故意的（信用卡月底扣款） |
| 第三圈「修正版上有一條不成立」 | 你寫的預期跟修正版不一樣 | 2 月沒有 31 號，用 2 月最後一天 2026-02-28；12 月加一個月是明年 1 月 |
| 第三圈「壞版本 2 沒抓到」 | 只試了 1 月 31 日 | 再試一個原本就好好的日子，例如 1 月 15 日 |
| 第三圈「壞版本 3 沒抓到」 | 沒試年底 | 寫一條 12 月加一個月 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-25 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、VS Code 與 GitHub 官方文件的原文、bug 回報範例、debugger 的其他按鈕）在 `補充.md`。
