# 0-5　裝 uv，跑起第一支 Python

這課大約 45 分鐘。三圈比例 75／20／5。

## 1. 題目

**第①圈：** 在自己的電腦用 uv 把帳本變成一個 Python 專案，跑起 `main.py`，然後下載課程資料夾、讓 check.py 記住你的帳本在哪裡。

- uv 是幫你安裝和管理 Python 的工具。這門課不用電腦內建的「系統 Python」，也不加 `sudo`。
- PATH 是電腦找指令的地方：你打 `uv`，電腦會照 PATH 裡的資料夾一個一個找。

**對答：** 錯誤訊息跟原因配對 3 題。

**第③圈：** 課程有一支 `doctor.py`，會印出三行「現在用的是哪一個 Python」。先不要跑它，寫下「在你的帳本裡，它應該印出什麼」。課程藏了 3 個寫錯的 doctor.py，其中一個會說你用的是系統 Python。你寫的預期要把壞的抓出來。

## 2. 提示

- 判斷一行安裝指令能不能信：網址是不是官方網域、是不是 `https://`。uv 的官方網站是 `https://docs.astral.sh/uv/`，安裝指令裡的網址是 `astral.sh`，兩個都是 astral 這家公司的網域。
- 剛裝好 uv，打 `uv --version` 說找不到指令？先關掉終端機、開一個新的視窗再試。這就是 PATH 還沒更新。
- `uv init --no-package --vcs none --python 3.13`：`--no-package` 是用最簡單的專案結構；`--vcs none` 是先不要建 git（0-7 才自己建）。`--python 3.13` 是指定用 3.13：電腦上如果已經有更新的 Python，不寫的話 uv 會挑最新那一版，下一行的 pin 3.13 就會被拒絕。
- uv init 會在帳本裡建出幾個檔案：`main.py` 是你的第一支程式；`pyproject.toml` 是這個專案的設定檔（專案叫什麼名字、要用哪一版 Python）。第一次 `uv run` 還會多出一個 `.venv` 資料夾：那是 uv 在帳本裡幫你放的一份專用 Python（叫做「虛擬環境」），`uv run` 會用它，不會去用電腦內建的。
- 網路上的教學叫你加 `sudo`，這門課都不要加。
- 卡住的時候，把「我打的指令＋完整的錯誤訊息＋我試過什麼」一起貼給白海豹（你的 AI 家教），不要只說「不能跑」。

## 3. 開始前要打的指令

**Mac 先裝 Command Line Tools。** 這是蘋果提供的一組開發工具，裡面有 git。打：

```bash
xcode-select --install
git --version
```

會跳出一個視窗問你要不要安裝，按「安裝」，等它跑完。如果已經裝過，終端機會印出這段英文，意思是「已經裝好了」，可以直接往下：

```
xcode-select: note: Command line tools are already installed. Use "Software Update" in System Settings or the softwareupdate command line interface to install updates
```

**裝 uv。** 打開 uv 的官方網站 `https://docs.astral.sh/uv/`，找到安裝那一段，對照網址是不是 `astral.sh`，再貼上這一行：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

裝好以後，**關掉終端機、開一個新的視窗**，然後：

```bash
uv --version
mkdir -p ~/code/ledger
cd ~/code/ledger
uv init --no-package --vcs none --python 3.13
uv python pin 3.13
uv run main.py
```

**下載課程資料夾。** 在課程的 GitHub 頁面按綠色的「Code」→「Download ZIP」。解壓縮以後，資料夾的名字會是 `plusform-course-main`，而且多半在「下載項目」裡。把它搬到 `~/code/`、名字改成 `plusform-course`：

```bash
mv ~/Downloads/plusform-course-main ~/code/plusform-course
```

（也可以用 Finder：把資料夾拖到「code」資料夾裡，再按一下名字改成 `plusform-course`。）

然後：

```bash
cd ~/code/plusform-course
uv run check.py setup ~/code/ledger
uv run check.py start 0-5
uv run check.py start 0-4
```

**打開作答檔。** 作答檔是純文字檔，可以用 Mac 的「文字編輯」打開來改，改完按 ⌘S 存檔（0-6 裝好 VS Code 以後就改用 VS Code）：

```bash
open -e ~/code/ledger/lessons/0-5/error_match.txt
open -e ~/code/ledger/lessons/0-5/doctor_expected.txt
```

Windows 用記事本：`notepad ~/code/ledger/lessons/0-5/error_match.txt`。

## 4. 成品示範

```
$ uv run main.py
Hello from ledger!
```

```
━━ 0-5  裝 uv，跑起第一支 Python ━━
這課大約要花 45 分鐘。
這次一共要檢查 13 題。先猜猜看：你覺得會過幾題？（0–13）：10

結果：過了 13／13 題
  ✓ 官方測試  5／5
  ✓ 對答  3／3
  ✓ 第③圈  5／5
  你的檢查把 3 個壞版本全部抓到了。

✓ 全部 13 題都過了！
你猜 10 題，實際過了 13 題：低估了 3 題（其實你比自己想的好）。
```

## 5. 怎麼測

在課程資料夾裡打 `uv run check.py 0-5`（或 `uv run check.py env`）。它會檢查：

- 帳本是 uv 專案（有 `pyproject.toml`）
- Python 釘在 3.13（`.python-version`）
- `uv run main.py` 印得出 `Hello from ledger!`
- 用的是帳本自己 `.venv` 裡的 Python 3.13，不是電腦內建的系統 Python
- 順便補驗 0-4 的資料夾結構還在
- 對答 3 題（答案在 `answers/error_match.json`）
- 第③圈：你寫的三行預期，在正確版的 doctor.py 上全部對，在 3 個壞版本上至少錯一行。沒對上的時候，check.py 只會告訴你是哪一行、該寫成什麼格式，不會直接給答案。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `zsh: command not found: uv` | 終端機還找不到 uv（PATH 還沒更新） | 關掉終端機、開新視窗再打一次 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course`；或在任何地方打完整路徑 `uv run ~/code/plusform-course/check.py 0-5` |
| `cd: no such file or directory: /Users/…/code/plusform-course` | 課程資料夾還沒搬好（可能還叫 `plusform-course-main`、還在「下載項目」裡） | 照上面的 `mv` 那一行搬過去 |
| `check.py 要用 Python 3.13 跑` | 你打了 `python3 check.py` | 改打 `uv run check.py ……` |
| `Project is already initialized` | 帳本裡已經有 `pyproject.toml` 了 | 不用再 `uv init`，直接往下做 |

## 6. 怎麼交

不用交給任何人。作答檔放在你的帳本裡：

- `~/code/ledger/lessons/0-5/error_match.txt`：每題的「答：」後面寫 A、B 或 C
- `~/code/ledger/lessons/0-5/doctor_expected.txt`：把三個「？」換成你的答案（冒號前面的字不要改）

全部通過就會記在 `~/code/ledger/.check/` 裡。
