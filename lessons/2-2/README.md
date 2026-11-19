# 2-2　套件與虛擬環境：uv add、pyproject、uv.lock

這課大約 45 分鐘。三圈比例 45／30／25。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：uv 專案與 uv run（0-5）、存檔點（0-7）、import（1-21）、class 的方法（1-24）、2-1 的交辦與核准（先存檔、指令看懂才按同意）。

2-1 的報表對齊了。這個月熊多記了一種分類「日用品」，三個字，報表又歪了。這一課第一次**裝別人寫好的套件**（rich），學會三件事：
**用 `uv add` 裝套件（寫進 pyproject.toml、記進 uv.lock）；裝之前到 PyPI 查清楚；交給 agent 以後，驗收它怎麼裝套件，在乾淨複本上跑過才收。**

## 1. 題目

**第①圈：自己來（看問題、查套件、uv add、uv sync）。**

A. 先看問題。在帳本資料夾跑一次：

```bash
uv run lessons/2-2/report.py
```

`日用品` 那一行的金額，比別行往右多了兩格。中文字在終端機佔兩格，`f"{category}  {amount:>5,} 元"` 只照「字數」補空格，三個字的分類就對不齊了。自己算寬度很麻煩，這種事有人寫好了：**套件**（別人寫好、放在網路上給大家裝的程式）。這課用 rich，它會畫表格，也會算中文字的寬度。

B. 裝之前，先到 PyPI 查它（寫 `pypi.md`）。

PyPI（Python Package Index，官方說念 pie pea eye，PI 一個字母一個字母念）是 Python 官方的套件倉庫，`uv add` 預設從這裡下載。打開 https://pypi.org/project/rich/ ，看三件事（頁面上寫的 `pip install rich` 不要照打，這門課一律用 `uv add`）：

1. **維護者**：右邊（手機在下面）的 maintainer，寫著誰在管這個套件。
2. **最近一次發布**：Key dates 的 Released（Release history 分頁有每一次的日期）。很久沒有更新的套件，出了問題可能沒人修。
3. **原始碼在哪裡**：Project links 的連結（rich 的 Homepage 連到 GitHub）。

維護者和發布日期旁邊標著 **PyPI data**，是 PyPI 自己的紀錄；Project links 是作者自己填的，沒有標 Verified 的就是 PyPI 沒驗證過，點進去看看是不是真的有在維護（PyPI 官方文件：沒標 PyPI data 或 Verified 的，都當成沒驗證過）。

**名字要一個字母一個字母對**：PyPI 上誰都可以放套件，PyPI 不先審查；有人會故意放名字很像的套件，等你拼錯（PyPI 官方文件稱 typosquatting）。AI 給你的套件名，一樣要查過（AI 可能編出一個不存在的名字，有人就搶先用那個名字放壞套件）。

別搞混：**PyPI ≠ PyPy ≠ PyPy 熊**。PyPI 是套件倉庫；PyPy 是另一種跑 Python 的程式（另一個 Python 直譯器）；PyPy 熊是這門課的熊。

C. 用 `uv add` 裝 rich。先猜：pyproject.toml 會多哪一行？再打：

```bash
uv add rich
```

它會印出裝了 4 個套件：rich，加上 rich 自己需要的 markdown-it-py、mdurl、pygments。打開 `pyproject.toml`，`dependencies = []` 變成：

```toml
dependencies = [
    "rich>=15.0.0",
]
```

意思是「這個專案要 rich，15.0.0 以上」（版本照你裝的那天）。`uv.lock` 也多了好幾段：rich 和它需要的每個套件，確切是哪個版本、從哪裡下載、檔案的指紋（hash）。

D. 刪掉 `.venv`，再裝回來：

```bash
rm -rf .venv
uv sync
```

`.venv` 是真的裝好套件的資料夾（虛擬環境）。刪掉以後，`uv sync` 照 uv.lock 一模一樣裝回來。所以 `.venv` 不用存：uv 在 `.venv` 裡放了一個 `.gitignore`，git 本來就不收它。

**第②圈：跟 AI 學（`deps.txt`）。** 問家教：「uv.lock 為什麼要放進存檔點？」先說你的想法，再聽它講；它說得對不對，用 uv 官方文件對一次。再做 `deps.txt` 3 題。

**第③圈：存檔，交給 agent，驗收它怎麼裝套件。**

1. 先按存檔點（原始碼控制面板，說明寫「交辦前」）。pyproject.toml、uv.lock 也一起存。
2. 在 Chat 選 Agent，交辦：

> 把 lessons/2-2/report.py 印出來的月報改成表格：用 rich 的 Table，分類靠左、金額靠右，日用品那一行也要對齊。rich 已經用 uv add 裝好了，只改 report.py。套件一律用 uv add，不要用 pip；要裝別的套件，先問我。改完用 uv run 跑一次給我看。

3. 它要執行指令時會先問你。**一個一個看懂再按同意**；它要裝套件，看它打的是不是 `uv add`。`pip install`、`uv pip install` 按拒絕，問它為什麼不用 uv add。
4. 驗收它怎麼裝套件：在原始碼控制面板看 pyproject.toml、uv.lock 有沒有變。變了，是它用 uv add 加的嗎？加了什麼？
5. 跑檢查（`uv run check.py 2-2`）：它會把你的 pyproject.toml、uv.lock、report.py 複製到一個沒有 .venv 的乾淨資料夾，打 `uv sync --locked` 重新裝一次，再跑 report.py。在你電腦跑得起來不算數，乾淨複本跑得起來才算。
6. 決定收不收，寫在 `decision.md`。收了，按 Keep，再按一個存檔點（說明寫「報表表格」）。

## 2. 提示

- **pyproject.toml、uv.lock、.venv 差在哪：** pyproject.toml 是你寫給 uv 的需求單（要 rich，15.0.0 以上）；uv.lock 是 uv 記下的確切版本（rich 15.0.0，還有它需要的每個套件）；.venv 是照 uv.lock 真的裝好的套件。前兩個要存進存檔點，.venv 不用（uv 官方文件：uv.lock should be checked into version control；不建議把 .venv 放進版本控制）。
- **uv.lock 不要手改：** 它由 uv 管理（官方文件：managed by uv and should not be edited manually）。要加套件打 `uv add`，要拿掉打 `uv remove`。
- **uv sync 會拿掉沒記在 uv.lock 的套件：** 用 `pip install` 或 `uv pip install` 裝進 .venv 的套件，下次打 `uv sync` 就被拿掉（官方文件：uv sync 預設 exact，會移除沒被選進來的套件）。
- **`uv sync --locked`：** uv.lock 跟 pyproject.toml 對不上（例如手改了 pyproject.toml），就停下來報錯，不會偷偷更新 uv.lock。check 的乾淨複本用的就是它。
- **uv tree：** 想看 rich 又需要哪些套件，打 `uv tree`，會畫出一棵樹。
- **裝錯了：** `uv remove 套件名`，pyproject.toml 和 uv.lock 會一起拿掉它。
- **rich 的表格：** `Table(title=…)` 做一張表、`add_column` 加一欄（`justify="right"` 靠右）、`add_row` 加一列、`Console().print(table)` 印出來。是 AI 交回來的寫法，讀得懂就好。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 2-2
```

它會把起點檔複製到你的帳本 `lessons/2-2/`：`report.py`、`pypi.md`、`deps.txt`、`decision.md`。

用 VS Code 打開帳本，在下面的終端機（帳本資料夾）打第 1 節的指令。檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 2-2
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 2-2`。）

## 4. 成品示範

```
$ uv run lessons/2-2/report.py
      11 月月報
┏━━━━━━━━┳━━━━━━━━━━┓
┃ 分類   ┃     金額 ┃
┡━━━━━━━━╇━━━━━━━━━━┩
│ 餐飲   │ 1,250 元 │
│ 交通   │   320 元 │
│ 日用品 │   448 元 │
│ 娛樂   │   480 元 │
│ 其他   │    95 元 │
│ 合計   │ 2,593 元 │
└────────┴──────────┘
```

表格的框線、標題長得不一樣沒關係（agent 寫的可能不同），每一列的分類靠左、金額靠右對齊就好。

## 5. 怎麼測

`uv run check.py 2-2` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。

第一圈：pyproject.toml 的 dependencies 和 uv.lock 都有 rich（用 uv add 裝的）；`pypi.md` 四個標籤寫了沒。第二圈：`deps.txt` 3 題。第三圈：乾淨複本上 `uv sync --locked` 裝得起來、report.py 印出對齊的表格（收下之前先驗收）；存檔點裡有 report.py 原本的樣子（交辦前存過檔），pyproject.toml、uv.lock、report.py 收下以後都存進存檔點；`decision.md` 五個標籤寫了沒。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| 「pyproject.toml 的 dependencies 裡還沒有 rich」 | 還沒裝，或用 pip 裝的 | 在帳本資料夾打 `uv add rich` |
| 「乾淨複本上跑 report.py，找不到 ○○ 這個套件」 | report.py 用了一個沒寫進 pyproject.toml 的套件（pip 或 uv pip install 裝的） | 在帳本資料夾打 `uv add ○○`，或請 AI 改回用 rich |
| 「uv sync --locked 停下來了：uv.lock 跟 pyproject.toml 對不上」 | pyproject.toml 手改過，uv.lock 沒更新 | 在帳本資料夾打 `uv lock`，以後用 `uv add`／`uv remove` |
| 「表格還沒對齊」 | 還是用空格硬排，中文字寬度沒算對 | 把 check 說的那一行貼回給 AI，請它用 rich 的 Table |
| `uv.lock 改過之後還沒按存檔點` | 收下了，可是還沒存 | 按 Keep 以後，再按一個存檔點（uv.lock 也要勾到） |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「2-2 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（uv、PyPI 官方文件的原文、影片裡家教的完整對話、agent 實際做了什麼）在 `補充.md`。
