# 0-8　跟 AI 學的正確姿勢：白海豹的家教協定

這課大約 40 分鐘。三圈比例 75／20／5。家教協定的全文在 [家教協定.txt](家教協定.txt)；完整的 AI 對話逐字紀錄、Windows 與桌面 App、ChatGPT 的做法、名詞小抄和官方來源，寫在 [補充.md](補充.md)。

## 1. 題目

**第①圈：** 把 AI 設成家教。在 Claude 網頁版建一個專案（Project），把家教協定貼進專案的 **Instructions**，按 **Save instructions** 存起來。這個專案裡的每一個對話都會參考它。

- 家教協定只是一段寫給 AI 的指示，不是鎖：想改就按 Instructions 旁邊的筆，刪掉就回到一般的樣子。
- 免費帳號也能建專案，最多 5 個（Claude 官方說明）。
- Claude 桌面 App 和網頁版是同一個帳號：登入以後，對話和專案都是同一份（Claude 官方下載頁）。
- 用 ChatGPT 的同學：同一段家教協定貼在對話的第一則訊息，一樣能用（細節看補充.md）。

**對答：** 4 題，寫在 `lessons/0-8/quiz.txt`。

**自評：** 跟你的家教聊一題，把對話貼進 `lessons/0-8/selfcheck.txt`，用四格清單自評（不對答案，只給你自己看）。

**第②圈（影片示範）：** 白海豹的三步協定：貼上自己的嘗試（指令＋完整錯誤訊息＋試過什麼）→ 請 AI 找錯、不給答案 → 自己改。另一種用法是「帶我寫」（Lead-and-Reveal）：每一步你先說要做什麼，AI 才給那一步的寫法。

**第③圈（影片示範）：** 時間規則（用 AI 幾分鐘就全對，是警訊）；不貼給 AI 的三樣東西：密碼、個資、真的帳單。

## 2. 提示

- 不要問「直接給我正確的指令」：AI 會替你做完，換一題你還是不會。
- 它還是直接給了答案：回一句「請照家教協定，先不要給答案，只指出我錯在哪裡」。
- 貼東西給 AI 之前，看一眼裡面有沒有密碼、個資（身分證字號、地址、電話）、真的帳單或卡號。練習一律用課程的假資料。
- 用 AI 幾分鐘就全部做對：關掉 AI，自己再做一次。
- Claude 的「Learning」這類選單常常改，這門課不依賴它，用自己寫的家教協定。

## 3. 開始前要打的指令

> 起點：0-7 的帳本（`~/code/ledger`，已經有兩個存檔點）和用 `git clone` 下載的課程資料夾。要有 Claude 或 ChatGPT 的帳號（免費的就可以，照官方網站的步驟自己註冊、登入）。

**在 Claude 網頁版（claude.ai）：**

1. 左邊的 **Projects** → **New project**。
2. 上面那一格寫專案的名字（例如「PyPy 熊的程式家教」），按 **Create project**。
3. 專案頁面的 **Instructions** 按 **+**，把 `家教協定.txt` 的全文貼進去，按 **Save instructions**。
4. 在這個專案裡開對話問問題（專案頁面上面的輸入框）。

**拿作答檔：**

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 0-8
code ~/code/ledger/lessons/0-8/quiz.txt
code ~/code/ledger/lessons/0-8/selfcheck.txt
```

寫好、存檔以後，到 VS Code 的原始碼控制寫一句說明、按 **Commit**（存檔點）。

## 4. 成品示範

Claude 專案頁面的 Instructions 這一格，會出現你貼的家教協定：

```
Instructions
你是我的程式家教。我剛開始學 Python，請用繁體中文回答。 1. 我來問問題時，先問我試了什麼……
```

在這個專案裡問「我打 uv run mian.py 出現錯誤……我試過再打一次」，它會先問你、指出要對照的地方，不直接給 `uv run main.py`（實際的回答每次不一樣，影片的逐字紀錄在補充.md）。

## 5. 怎麼測

在課程資料夾裡打 `uv run check.py 0-8`。它會檢查對答 4 題（答案在 `answers/quiz.json`）。`selfcheck.txt` 是自評，check.py 不看。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| 找不到 Projects | 介面改版或視窗太窄，側欄收起來了 | 按左上角打開側欄；或直接打網址 claude.ai/projects |
| 已經有 5 個專案，建不了新的 | 免費帳號最多 5 個專案 | 把用不到的專案刪掉（專案右上角的 … → Delete），或把協定貼在對話的第一則訊息 |
| 它還是直接給了答案 | 協定只是指示，AI 不一定每次都照做 | 回一句「請照家教協定，先不要給答案」 |
| `lessons/0-8/quiz.txt` 找不到 | 還沒拿作答檔 | 在課程資料夾打 `uv run check.py start 0-8` |

## 6. 怎麼交

不用交給任何人。作答檔放在你的帳本裡：

- `~/code/ledger/lessons/0-8/quiz.txt`：每題的「答：」後面寫 A、B、C 或 D
- `~/code/ledger/lessons/0-8/selfcheck.txt`：一段跟家教的對話＋四格自評（只給你自己看）

全部通過就會記在 `~/code/ledger/.check/` 裡（這個資料夾不會進存檔點）。
