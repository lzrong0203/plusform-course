# 0-7　存檔點：讓 AI 改壞了也不怕

這課大約 30 分鐘。三圈比例 75／20／5。每一步在做什麼、畫面跟影片不一樣怎麼辦、Windows 的做法、名詞小抄和官方來源，寫在 [補充.md](補充.md)。

## 1. 題目

**第①圈：** 幫你的帳本按存檔點。先告訴 git 你是誰（名字和信箱），在 VS Code 的「原始碼控制」按 **Initialize Repository** 建立存放庫，按下第一個存檔點（Commit）。接著故意改壞 `main.py`、看紅綠差異，再按 **Discard Changes** 退回存檔點。

- 存檔點就像玩遊戲打王之前的存檔：把整個資料夾在那一刻的樣子記下來，之後改壞了還回得去。幫你記存檔點的工具叫 git（Mac 在 0-5 跟著 Command Line Tools 裝好了；Windows 在 0-W 第 1 章裝好了）。
- 按 ⌘S 只是把檔案存起來，**不是**存檔點。

**對答：** 4 題「改壞了怎麼回去」，寫在 `lessons/0-7/quiz.txt`。寫好以後按第二個存檔點。

**第③圈（影片示範）：** 讓 agent 改程式之前先按存檔點；交出去之前先寫下「差異應該長怎樣」，改完再看紅綠差異，對不上就 Discard。

**課程資料夾改用 git：** 0-5 用 Download ZIP 下載的課程資料夾，換成 `git clone` 下載的版本，以後用 `git pull` 更新。

## 2. 提示

- 信箱會寫進你以後的每一個存檔點。以後把程式放上 GitHub（3-3），舊的存檔點都會帶著它，別人看得到。所以現在先填一個你不介意公開的信箱；2-1 開好 GitHub 帳號後，換成 GitHub 給你的 noreply 信箱。
- 名字中間有空格，前後要用引號包起來：`"PyPy Bear"`。
- 設好名字和信箱，終端機什麼都不印，就是設好了。
- 按 Commit 時跳出「There are no staged changes to commit…」，按 **Yes**（把所有改動一起存進去）。
- **Publish to GitHub**、**Publish Branch** 是放上網路用的，這課都先不要按。
- Discard 丟掉的改動不會進垃圾桶，不保證救得回來；不確定就先別按。
- 讓 AI 改程式之前，先按一個存檔點。

## 3. 開始前要打的指令

> 起點：0-6 的帳本（`~/code/ledger`），已經用 VS Code 打開過。Windows：指令都在 Git Bash 照打，⌘ 換成 Ctrl。

**告訴 git 你是誰（只要做一次）。** 名字和信箱換成你自己的：

```bash
git config --global user.name "你的名字"
git config --global user.email 你不介意公開的信箱
```

**在 VS Code 裡（帳本打開的狀態）：**

1. 左邊像樹枝分岔的圖示＝原始碼控制（Source Control），按下去。
2. 按 **Initialize Repository**（等於 `git init`）。
3. 上面的框寫一句說明（例如「第一個存檔點」），按 **Commit**，跳出的問題按 **Yes**。
4. 故意刪掉 `main.py` 第二行最後的右括號，按 ⌘S 存檔。原始碼控制的清單會出現 `main.py`，旁邊寫 M。
5. 在下面的終端機打 `uv run main.py`，會看到錯誤訊息（最後一行說括號沒有關起來）。
6. 按清單裡的 `main.py` 看差異：左邊是存檔點的樣子，右邊是現在的樣子。
7. 滑到 `main.py` 那一列，按往回轉的箭頭（**Discard Changes**），再按 **Discard File**。再跑一次 `uv run main.py`，`Hello from ledger!` 又出現了。

**課程資料夾換成 git 下載的版本。** 在課程的 GitHub 頁面按綠色的 **Code**，複製 HTTPS 那一格網址，然後：

```bash
cd ~/code
mv plusform-course plusform-course-old
git clone https://github.com/lzrong0203/plusform-course.git
cd plusform-course
git pull
uv run check.py start 0-7
```

（`plusform-course-old` 是 0-5 下載的舊版，確定新的能用以後再丟掉。對答案程式記的是帳本的位置，換掉課程資料夾，進度不會不見。）

**打開作答檔：**

```bash
code ~/code/ledger/lessons/0-7/quiz.txt
```

寫好、存檔以後，回到 VS Code 的原始碼控制，寫一句說明、按 **Commit**（第二個存檔點）。

## 4. 成品示範

VS Code 原始碼控制下面的 Graph，會有兩個圓點：

```
○ 寫好作答檔        你的名字
○ 第一個存檔點      你的名字
```

```
$ git pull
Already up to date.
```

## 5. 怎麼測

在課程資料夾裡打 `uv run check.py 0-7`。它會檢查：

- 帳本是 git 存放庫（有 `.git` 資料夾）
- 至少有 2 個存檔點
- 作答檔 `lessons/0-7/quiz.txt` 寫好之後也存進存檔點了
- 對答 4 題（答案在 `answers/quiz.json`）

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `Make sure you configure your "user.name" and "user.email" in git.` | git 不知道你是誰 | 照第 3 節打那兩行 `git config --global`，再按一次 Commit |
| `Author identity unknown` `*** Please tell me who you are.` | 同上（終端機的版本） | 同上 |
| 帳本現在有 1 個存檔點，這一關要至少 2 個 | 還差一個存檔點 | 寫好作答檔、存檔，在原始碼控制寫說明、按 Commit |
| lessons/0-7/quiz.txt 改過之後還沒按存檔點 | 作答檔存了（⌘S）但還沒按 Commit | 到原始碼控制按 Commit |
| `fatal: destination path 'plusform-course' already exists and is not an empty directory.` | `~/code` 裡已經有 `plusform-course`（舊的 ZIP 版還沒改名） | 先打 `mv plusform-course plusform-course-old`，再 clone |
| `fatal: not a git repository` | 在 ZIP 版的課程資料夾裡打 `git pull` | 換成 `git clone` 下載的版本（第 3 節） |

## 6. 怎麼交

不用交給任何人。作答檔放在你的帳本裡：

- `~/code/ledger/lessons/0-7/quiz.txt`：每題的「答：」後面寫 A、B 或 C，寫好後按 Commit

全部通過就會記在 `~/code/ledger/.check/` 裡（這個資料夾不會進存檔點）。
