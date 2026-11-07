# 0-4　終端機不可怕，順便看懂 agent 要跑的指令

這課大約 40 分鐘。三圈比例 75／20／5。

## 1. 題目

**第①圈：自己打指令。** 在帳本資料夾 `~/code/ledger` 裡，只用終端機做出這個樣子：

```
ledger/
├── data/
│   └── receipts/
├── notes/
│   ├── todo.txt
│   └── hello_copy.txt
└── practice/
    ├── hello.txt
    └── final.txt
```

做的過程中要用到 `mkdir -p`（建資料夾）、`touch`（建空檔案）、`cp`（複製）、`mv`（搬家或改名）、`rm`（刪除）。最後 `practice/` 裡不能有 `draft.txt` 和 `trash.txt`：一個要改名成 `final.txt`，一個要刪掉。

**第③圈：agent 要跑指令，你來把關。**

- 權限判斷 3 題：agent 想跑 `ls -a`、`mkdir -p data/2026`、`rm -rf ../`，各要允許還是拒絕？
- 讀一段 agent 想跑的 6 行指令（`agent_setup.txt`），裡面藏了一行 `rm -rf`。它故意存成 `.txt`，只讓你讀、不讓你跑。照下面的需求卡，寫出「做完之後帳本應該長什麼樣子」的檢查。

需求卡（你交給 agent 的）：

| 欄位 | 內容 |
|---|---|
| 目標 | 在帳本裡建 11 月的預算資料夾 |
| 背景 | 帳本裡已經有第①圈建好的 `data/`、`notes/`、`practice/` |
| 限制 | 原本的東西一個都不能動 |
| 怎樣算做完 | 有 `budget/2026-11/food.txt`、`budget/2026-11/bus.txt`，還有一份 `notes/todo.txt` 的副本 `budget/todo_copy.txt` |

## 2. 提示

- 每打一個指令之前，先猜它會做什麼，再按 Enter。
- `mkdir -p a/b` 的 `-p` 是「上一層不存在就一起建」。少了 `-p`，`a` 不存在時就會失敗。
- `rm` 刪掉的檔案**不會進垃圾桶**。刪之前先 `ls` 看清楚。
- `..` 是上一層。`rm -rf ../` 會把帳本的上一層整個刪掉。
- 路徑打一半按 Tab，終端機會幫你補完，比較不會打錯字。按 ↑ 可以叫出上一個指令，按 Ctrl+C 可以停下正在跑的東西。
- 看到 `No such file or directory`，意思是「找不到這個檔案或資料夾」：通常是打錯字，或是你不在你以為的位置（打 `pwd` 看看現在在哪裡）。
- 第③圈的檢查，除了「該有的有沒有」，也想想「原本就有的東西，跑完還在嗎？」。

## 3. 開始前要打的指令

0-4 的時候你還沒有課程資料夾，這很正常。先打開終端機：

```bash
mkdir -p ~/code/ledger
cd ~/code/ledger
pwd
```

第①圈照影片一步一步打（下面是一種做法，順序可以不一樣）：

```bash
mkdir -p data/receipts notes practice
touch notes/todo.txt practice/hello.txt practice/draft.txt practice/trash.txt
cp practice/hello.txt notes/hello_copy.txt
mv practice/draft.txt practice/final.txt
rm practice/trash.txt
ls -R
```

0-5 裝好 uv、下載課程資料夾以後，回到課程資料夾拿第③圈的作答檔：

```bash
cd ~/code/plusform-course
uv run check.py start 0-4
```

作答檔是純文字檔。Mac 可以用「文字編輯」打開來改，改完按 ⌘S 存檔：

```bash
open -e ~/code/ledger/lessons/0-4/permissions.txt
open -e ~/code/ledger/lessons/0-4/checks.txt
```

（0-6 裝好 VS Code 以後，就改用 VS Code 打開。Windows 可以用記事本：`notepad 檔名`。）

## 4. 成品示範

在帳本資料夾裡打 `ls -R`，應該看到（排版可能是橫的或直的，名字一樣就對了；Windows 的 Git Bash 最前面會多一行 `.:`）：

```
data		notes		practice

./data:
receipts

./data/receipts:

./notes:
hello_copy.txt	todo.txt

./practice:
final.txt	hello.txt
```

全部做完以後，`uv run check.py 0-4` 會長這樣：

```
━━ 0-4  終端機不可怕，順便看懂 agent 要跑的指令 ━━
這課大約要花 40 分鐘。
這次一共要檢查 9 題。先猜猜看：你覺得會過幾題？（0–9）：8

結果：過了 9／9 題
  ✓ 對答  4／4
  ✓ 第③圈  5／5
  你的檢查把 3 個壞版本全部抓到了。

✓ 全部 9 題都過了！
你猜 8 題，實際過了 9 題：差 1 題，很準。
```

## 5. 怎麼測

- **0-4 當下：** 自己用 `ls -R` 的輸出，對照說明欄（或 `answers/ls_R.txt`）的標準答案。權限 3 題也對照說明欄的答案。
- **0-5 做完以後：** 在課程資料夾裡打 `uv run check.py 0-4`，它會補驗：
  - 帳本資料夾的結構對不對（對答）
  - 權限判斷 3 題（對答，答案在 `answers/permissions.json`）
  - 第③圈：你寫的檢查，要在 agent 的正確版上全部通過，在 3 個壞版本上至少有一條不通過。agent 的指令**不會真的跑**，check.py 只在一個假的資料夾裡模擬。

## 6. 怎麼交

不用交給任何人。作答檔放在你的帳本裡：

- `~/code/ledger/lessons/0-4/permissions.txt`：每題的「答：」後面寫「允許」或「拒絕」
- `~/code/ledger/lessons/0-4/checks.txt`：一行一條檢查（路徑；資料夾結尾加 `/`；「應該不見」的前面加 `沒有 `）

`uv run check.py 0-4` 全部通過，就會記在 `~/code/ledger/.check/` 裡。
