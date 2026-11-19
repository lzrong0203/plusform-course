# 2-3　測試先行：pytest

這課大約 50 分鐘。三圈比例 45／30／25。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：assert（1-8）、分帳的 // 和 %（1-4）、def 與 return（1-18）、lambda（1-20）、import（1-21）、raise（1-22）、@dataclass 的 @（1-24）、uv add（2-2）、2-1 的交辦與核准（先存檔、指令看懂才按同意）。

第 1 級寫的檢查，是一條一條寫在最外層的 assert：第一條不成立，程式就停了，後面的根本沒跑。這一課換成 **pytest**（Python 最常用的測試工具），學會三件事：
**先寫測試、看它紅，再改程式讓它變綠；用 parametrize 一次測很多組、用 monkeypatch 換掉「今天」；審 AI 寫的測試，用壞版本試它抓不抓得到錯。**

## 1. 題目

**第①圈：自己來（裝 pytest、搬 assert、先紅後綠、parametrize、monkeypatch）。**

A. 先看第 1 級的寫法。熊把 1-4 的分帳改成「幾個人都能分」（`split.py`），可是零頭還沒放進去。在帳本資料夾跑：

```bash
uv run lessons/2-3/checks_split.py
```

它在第 5 行停下來（AssertionError），沒說算出來是多少；第 6 行根本沒跑。

B. 裝 pytest。它是寫程式的時候才用的工具，用 `--dev` 裝（uv 官方文件：development dependencies 只在你自己的電腦用）：

```bash
uv add --dev pytest
```

`pyproject.toml` 多了 `[dependency-groups]` 的 `dev = ["pytest>=9.2.0"]`（版本照你裝的那天）。uv run 預設也會裝好 dev 這一組，所以 `uv run pytest` 直接能跑。

C. 把 assert 搬進 `tests/test_split.py`。pytest 會找檔名 `test_` 開頭的檔，裡面名字 `test_` 開頭的函式就是一個測試（官方文件：test prefixed test functions）。起點檔已經搬好第一條，把另外兩條也搬過來：

```python
def test_leftover():
    assert split(100, 3) == [34, 33, 33]
```

在帳本資料夾打（不用加檔名，pytest 自己找）：

```bash
uv run pytest
```

**先紅**：它會跑完全部，印出 `1 failed, 2 passed`，還寫出算出來是 `[33, 33, 33]`。紅色是好事：測試抓到程式還沒做到的事。

**後綠**：打開 `split.py`，在 `return shares` 上面加兩行（零頭從第一個人開始，一人多 1 元）：

```python
    for i in range(total % people):
        shares[i] = shares[i] + 1
```

存檔，再打一次 `uv run pytest`，變成 `3 passed`。

D. 零頭的情況很多（101 元、10 元四個人、1 元三個人…），一個一個寫 def 太長。改成 **parametrize**：同一個測試，用好幾組資料各跑一次。

```python
import pytest

from split import split


@pytest.mark.parametrize("total, people, expected", [
    (300, 3, [100, 100, 100]),
    (100, 3, [34, 33, 33]),
    (101, 3, [34, 34, 33]),
    (100, 4, [25, 25, 25, 25]),
    (10, 4, [3, 3, 2, 2]),
    (1, 3, [1, 0, 0]),
])
def test_split(total, people, expected):
    assert split(total, people) == expected
```

def 上面、`@` 開頭的那一行叫**裝飾器**：幫下面的函式加上一層功能（1-24 的 `@dataclass` 也是）。這裡的意思是「下面這個測試，用這六組資料各跑一次」，每一組的三個值，照順序放進 total、people、expected。`uv run pytest -v` 會一組一列印出來（方括號裡是那一組的資料）。

E. 換掉「今天」（`tests/test_dates.py`）。`dates.py` 的 `fill_date("")` 會用今天的日期（記帳時日期直接按 Enter）。測試寫 `== "11/03"`，只有 11 月 3 日會過。用 **monkeypatch** 把今天換成固定的一天：

```python
def test_empty_means_today(monkeypatch):
    monkeypatch.setattr(dates, "today", lambda: date(2026, 11, 3))
    assert dates.fill_date("") == "11/03"
```

測試函式的參數寫 `monkeypatch`，pytest 就會交給你這個工具；`setattr` 把 dates 裡的 `today` 換成一個永遠回答 2026 年 11 月 3 日的小函式（lambda，1-20）。這個測試跑完，pytest 會自動換回來（官方文件：All modifications will be undone after the requesting test function or fixture has finished）。

**第②圈：跟 AI 學（`edges.md`）。** 問家教：「我的 test_split 有六個案例，都過了。我漏了哪些邊界情況？用問題帶我想，一次問一題。」先說你的想法，再聽它講。它提的每一條，自己決定：**加、不加、還是先問需求**，寫在 `edges.md`（至少三條）。

人數是 0 這一條，需求卡寫了「人數至少 1 個人」，所以要加，而且**先寫測試**：

```python
def test_no_people():
    with pytest.raises(ValueError):
        split(100, 0)
```

`pytest.raises(ValueError)` 的意思是「下面這一行應該丟出 ValueError」。先跑一次：紅（它丟的是 ZeroDivisionError）。再在 `split` 的第一行加：

```python
    if people < 1:
        raise ValueError(f"人數至少要 1 個人：{people}")
```

再跑一次：綠。

**第③圈：存檔，請 AI 寫測試，你來審。**

1. 先按存檔點（原始碼控制面板，說明寫「交辦前」）。
2. 在 Chat 選 Agent，交辦：

> 幫 lessons/2-3/monthly.py 的 monthly_total 寫 pytest 測試，放在 lessons/2-3/tests/test_monthly.py。不要改 monthly.py，不要裝任何套件（pytest 已經用 uv add --dev 裝好了）。寫完用 uv run pytest 跑一次，把輸出貼給我。

3. 它要執行指令時會先問你，一個一個看懂再按同意。它沒附 pytest 的輸出，就不算做完。
4. **審它的測試**（`review.txt` 2 題，看的是課程凍結的 `ai_test_monthly.py`）：有沒有「永遠會過」的測試？期望值是自己手算的，還是照程式的算法算出來的？
5. 跑檢查：`uv run check.py 2-3` 會拿 4 個寫錯的 monthly_total 跑你的 test_monthly.py。課程凍結的 AI 測試只抓得到 1 個。
6. 改到 4 個都抓到：期望值自己手算（例如 120 加 15 是 135）；帳裡要有別的月份、要有 1 月；一筆都沒有是 0。
7. 決定收不收，寫在 `decision.md`。收了，再按一個存檔點（說明寫「月合計測試」）。

沒開 GitHub 帳號的同學：在帳本資料夾打 `cp lessons/2-3/ai_test_monthly.py lessons/2-3/tests/test_monthly.py`，從第 4 步做起（也可以把交辦的話貼給聊天版 AI，把它寫的測試貼進去）。

## 2. 提示

- **pytest 印的符號：** `.` 是過了、`F` 是沒過；最後一行 `1 failed, 2 passed` 是總數。沒過的那一個，會印出 `assert [33, 33, 33] == [34, 33, 33]`：左邊是算出來的，右邊是你寫的。
- **紅色先出現是對的：** 先寫測試、跑一次確定它會紅，再寫程式讓它變綠。沒紅過的測試，你不知道它抓不抓得到錯。
- **`uv run pytest -v`：** 每個測試一行；parametrize 的每一組也各一行。
- **`__pycache__`、`.pytest_cache`：** 跑過 pytest 以後自動多出來的暫存資料夾，不用管，也不用存（`.pytest_cache` 自己帶了 .gitignore，git 本來就不收）。
- **conftest.py：** 課程準備的空檔，有它 pytest 才找得到同一個資料夾的 `split.py`。不用改，也不要刪。
- **tmp_path（延伸）：** 要測寫檔案的函式，測試函式的參數寫 `tmp_path`，pytest 會在測試開始前給你一個這個測試專用的暫存資料夾（官方文件：a temporary directory unique to each test function），例如 `path = tmp_path / "ledger.txt"`。這課的 check 不考，1-23 的 save／load 可以拿來練。
- **期望值要自己手算：** 測試的期望值抄程式的算法，程式的想法錯了，測試也跟着錯。帳裡只有 11 月，挑錯月份的程式也測不出來。
- **第 2 級交辦給 agent 的三條規矩：** 它不能改 `tests/`（除非你請它寫測試）、不能用 pip 裝套件、沒附測試的輸出不算做完。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 2-3
```

它會把起點檔複製到你的帳本 `lessons/2-3/`：`split.py`、`checks_split.py`、`dates.py`、`monthly.py`、`ai_test_monthly.py`、`conftest.py`、`tests/test_split.py`、`tests/test_dates.py`、`edges.md`、`review.txt`、`decision.md`。

用 VS Code 打開帳本，在下面的終端機（帳本資料夾）打第 1 節的指令。檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 2-3
```

## 4. 成品示範

```
$ uv run pytest
============================= test session starts ==============================
collected 10 items

lessons/2-3/tests/test_dates.py ..                                       [ 20%]
lessons/2-3/tests/test_split.py .......                                  [ 90%]
lessons/2-3/tests/test_monthly.py ...                                    [100%]

============================== 10 passed in 0.03s ==============================
```

（第一行下面還有 platform、rootdir 這幾行；測試的個數照你寫的。）

## 5. 怎麼測

`uv run check.py 2-3` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。

第一圈：pytest 用 uv add --dev 裝了；`split.py` 的零頭修好了；`tests/test_split.py` 至少 6 個測試、正確版全部通過、抓到 3 個零頭寫錯的版本；`tests/test_dates.py` 用 monkeypatch 換掉今天、抓到 3 個寫錯的版本。第二圈：`edges.md` 三條寫了沒；`split(100, 0)` 丟出 ValueError；你的測試抓到「人數是 0 卻沒丟 ValueError」的版本。第三圈：`review.txt` 2 題；`tests/test_monthly.py` 至少 3 個測試、正確版全部通過、4 個寫錯的 monthly_total 都抓到；交辦前存過檔、改好的 test_monthly.py 存進存檔點；`decision.md` 寫了沒。

check 會把你的測試檔複製到暫存資料夾，各跑一次正確版和每個壞版本（用你帳本裡裝的 pytest），不會改你的檔。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 10 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `error: Failed to spawn: pytest` | 帳本還沒裝 pytest | 在帳本資料夾打 `uv add --dev pytest` |
| `ModuleNotFoundError: No module named 'split'` | pytest 找不到 split.py | `lessons/2-3/conftest.py` 被刪了：再打一次 `uv run check.py start 2-3` 補回來 |
| `collected 0 items` | pytest 沒找到測試 | 檔名和函式名稱都要用 `test_` 開頭 |
| 「○○ 在正確版上就沒過」 | 測試的期望值算錯了 | 正確版不會錯：再手算一次期望值 |
| 「溜過去了：…」 | 你的測試沒抓到這個壞版本 | 照提示多加一組資料（例如 1 月、別的月份、空的帳） |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「2-3 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（pytest 官方文件的原文、影片裡家教的完整對話、agent 實際寫了什麼）在 `補充.md`。
