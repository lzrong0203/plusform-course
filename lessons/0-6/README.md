# 0-6　裝 VS Code，打開你的專案

這課大約 40 分鐘。三圈比例 75／20／5。

> Windows：先看 0-W 第 3 章（裝 VS Code、內建終端機改成 Git Bash），再照這一節最後的「Windows」小節。

## 1. 題目

**第①圈：** 裝好 VS Code（寫程式用的編輯器），用它打開上一課的帳本 `~/code/ledger`，改一個字、存檔、跑起來。

- 第一次打開就先關掉內建的 AI。第①圈要練的是你自己寫得出來；AI 先幫你補完，就分不出哪些是自己會的。檢核的時候也要關。
- 裝 Microsoft 的 Python 擴充，確認 VS Code 右下角用的是帳本自己的 Python（`ledger (3.13…)`），不是 Mac 內建的系統 Python。

**對答：** 截圖判讀 2 題（`screen_read.txt`）。

**第③圈：** agent 說「VS Code 設好了」的時候，先寫下右下角應該看到什麼，再看一眼截圖。對不上就退回。

## 2. 提示

- 分頁上檔名旁邊的圓點，代表「改了，還沒存檔」。這時候跑程式，跑的還是舊的內容。
- 右下角的 Python 按一下，會列出所有找得到的 Python。帳本自己的那一份寫著 `.venv`；`/usr/bin/python3` 是 Mac 內建的系統 Python（VS Code 官方寫明不支援）。
- 第一次打開資料夾，上面會有一條「Restricted Mode（受限模式）」的橫幅。帳本是你自己建的，按 Manage → Trust；從網路下載、不認得的資料夾先不要按。
- 擴充搜尋 python 會跑出很多名字很像的，看作者是不是 **Microsoft**、旁邊有沒有藍色勾勾。
- 詳細步驟、設定的名字、官方出處：[補充.md](補充.md)。

## 3. 開始前要打的指令

先有上一課的帳本（`uv run main.py` 印得出 `Hello from ledger!`）。還沒做的，先做 0-5。

1. 照 VS Code 官方說明裝好 Mac 版：下載、打開 `.dmg`、把 Visual Studio Code 拖進「應用程式」、按兩下打開。
2. 關掉內建 AI：按 `⌘,` 打開設定，搜尋 `disable ai`，勾 **Chat: Disable AI Features**。
3. 加入 `code` 指令：按 `⌘⇧P`，打 `shell command`，選 **Shell Command: Install 'code' command in PATH**。然後**關掉終端機、開一個新的視窗**。
4. 打開帳本，按 Trust：

   ```bash
   cd ~/code/ledger
   code .
   ```

5. 左邊的方塊圖示（擴充）搜尋 `python`，裝作者是 Microsoft 的 **Python**。按 `main.py`，看右下角是不是 `ledger (3.13…)`。
6. 把 `main.py` 第二行引號裡的 `ledger` 改成 `PyPy`，按 `⌘S` 存檔，在下面的終端機（`⌃` 加反引號打開）打：

   ```bash
   uv run main.py
   ```

7. 自動存檔（選做）：設定搜尋 `auto save`，**Files: Auto Save** 選 `afterDelay`。

然後拿作答檔：

```bash
cd ~/code/plusform-course
uv run check.py start 0-6
```

### Windows

- 照 0-W 第 3 章裝 VS Code（安裝程式會把 `code` 加進 PATH，重開 Git Bash 就能打 `code .`）。
- **裝完先關掉 VS Code，從開始選單重新打開**，內建終端機才找得到 uv（0-W 在 Windows 11 實測：從安裝程式最後一頁直接開的 VS Code，終端機還是舊的設定）。
- 內建終端機的預設改成 Git Bash（0-W 第 3 章），其他指令照打。
- 右下角的 Python 一樣要是帳本的 `.venv`；Windows 的路徑寫成 `.venv\Scripts\python.exe`。

## 4. 成品示範

```
$ uv run main.py
Hello from PyPy!
```

```
━━ 0-6  裝 VS Code，打開你的專案 ━━
這課大約要花 40 分鐘。
這次一共要檢查 7 題。先猜猜看：你覺得會過幾題？（0–7）：6

結果：過了 7／7 題
  ✓ 官方測試  5／5
  ✓ 對答  2／2

✓ 全部 7 題都過了！
```

## 5. 怎麼測

在課程資料夾裡打 `uv run check.py 0-6`。它會檢查：

- 帳本還是 uv 專案、Python 釘在 3.13
- 帳本裡有 `.venv`
- `uv run main.py` 跑得起來（`Hello from ledger!` 或改過的 `Hello from PyPy!` 都算）
- 用的是 `.venv` 裡的 Python 3.13，不是系統 Python
- 對答 2 題（答案在 `answers/screen_read.json`）

VS Code 的設定（關掉 AI、選哪個 Python）存在 VS Code 裡，check.py 不檢查；請自己看右下角。

### 常見狀況

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `zsh: command not found: code` | 還沒加入 `code` 指令，或終端機還沒重開 | 照第 3 節第 3 步做，再開一個新的終端機 |
| 右下角寫 `Python 3.9.6` | 選到 Mac 內建的系統 Python | 按一下右下角，選寫著 `.venv` 的那一行 |
| 右下角沒有出現 Python | 還沒裝 Python 擴充，或沒打開 `.py` 檔 | 裝 Microsoft 的 Python 擴充，按一下 `main.py` |
| 上面一條 Restricted Mode 的橫幅 | 受限模式（第一次打開資料夾都會這樣） | 自己建的帳本：按 Manage → Trust |
| 跑出來還是舊的那一句 | 改了還沒存檔（分頁上有圓點） | 按 `⌘S`，再跑一次 |

## 6. 怎麼交

不用交給任何人。作答檔放在你的帳本裡：

- `~/code/ledger/lessons/0-6/screen_read.txt`：兩題的「答：」後面各寫一個英文字母（截圖 `q1_a.png`、`q1_b.png`、`q2.png` 在同一個資料夾，在 VS Code 左邊按一下就看得到）

全部通過就會記在 `~/code/ledger/.check/` 裡。
