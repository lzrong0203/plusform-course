# 2-1　開 GitHub 帳號，第一次讓 AI 碰你的專案

這課大約 50 分鐘（開帳號、開兩步驟驗證另外算）。三圈比例 45／30／25。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：存檔點（0-7）、終端機指令 ls、rm（0-4）、uv run（0-5）、VS Code（0-6）、dict 加總（1-15）、f-string（1-5）。

從這一課起是第 2 級：AI 第一次碰你的專案檔。第 1 級的 AI 只當家教，不碰你的檔案；這一課開始，VS Code 裡的 Copilot 可以用 agent 模式幫你改檔、跑指令。
規矩只有三條：**交給它之前先存檔；它要執行的指令，看懂才按同意；改完看 diff、跑檢查，由你決定收不收。**

## 1. 題目

**第①圈：自己來（帳號、信箱、登入、預期輸出）。**

A. 開 GitHub 帳號，開兩步驟驗證（照 GitHub 官方文件，影片裡用官方文件的畫面講步驟）：

1. 到 https://github.com/signup 照畫面填，過程中要驗證信箱。信箱用你自己的，帳號名稱會公開。
2. 開兩步驟驗證（2FA）：右上角頭像 → Settings → 左邊 Password and authentication → Enable two-factor authentication → 用手機的驗證 App 掃 QR code，把 App 顯示的六位數填回去。
3. **復原碼（recovery codes）一定要下載、存好**：手機掉了，靠它才登得回來。

B. 把 git 的信箱換成 GitHub 給的 noreply 信箱：

1. GitHub 右上角頭像 → Settings → 左邊 Emails，確認 **Keep my email addresses private** 是 **On**（2026-11 的畫面是一個開關，沒開就按一下）。那一段會寫出一個 `一串數字+你的帳號@users.noreply.github.com` 的信箱，複製它。
2. 在 VS Code 的終端機打（換成你自己的那一個）：

```bash
git config --global user.email 一串數字+你的帳號@users.noreply.github.com
git config --global user.email
```

第一行成功時什麼都不印；第二行印出你剛剛設的信箱，就換好了。0-7 設的信箱會寫進每一個存檔點，之後推上 GitHub（3-3）就會公開；換成 noreply 信箱，別人只看得到這一串。以前按過的存檔點還是記舊的信箱，只有之後的用新的。

先不開帳號也可以：在 `account.md` 寫下原因，和第③圈改用哪一個免費的聊天版 AI（例如 0-8 的家教；兩欄都要寫），寫好再貼進 report.py。

C. 在 VS Code 打開 AI 功能、登入 Copilot Free：

1. 0-6 關掉的內建 AI 要打開：⌘ 逗號打開設定，搜尋 `disable ai`，把 **Chat: Disable AI Features** 的勾拿掉。
2. 下面狀態列的 Copilot 圖示 → 登入（用 GitHub 帳號）。瀏覽器會跳出授權頁，確認是 GitHub 的網址再按同意。還沒有 Copilot 方案的帳號，登入時會開成 Copilot Free（VS Code 官方文件）；登入好以後，按狀態列的 Copilot 圖示，最上面會寫 **Copilot Free**。
3. 打開右邊的 Chat（⌃⌘I），它就是 agent。輸入框下面寫 **Local**（在 VS Code 裡面跑的 agent；另一個 Cloud 要付費方案，不用選）；權限維持預設的 **Default permissions**（常見的唯讀指令可能直接跑，其他的指令會先停下來問你；Allow all、Autopilot 不會問你，先不要選）。

D. 先手寫預期輸出（`expected.txt`）。`report.py` 是熊的 11 月月報，跑起來數字沒有對齊：

```
11 月月報
餐飲 1250 元
交通 320 元
娛樂 480 元
其他 95 元
合計 2145 元
```

交給 AI 之前，先寫下「對齊以後應該長什麼樣子」，這就是驗收的標準。規則：第一行照舊；金額加千分位逗號（1250 寫成 1,250）、靠右對齊（每一行的最後一個數字對齊）；最寬的 1,250、2,145 跟分類中間空兩格；金額後面空一格接「元」。一個字、一個空格都要一樣。

**第②圈：跟 AI 學（`commands.txt`）。** 請家教出幾行 agent 可能會要執行的指令，每一行先問你「這行指令會做什麼？」，你先說、它再講。再做 `commands.txt` 4 題：它要執行的這一行會做什麼、按同意還是拒絕。

**第③圈：存檔，交給 agent，再驗收。**

1. 先按存檔點（原始碼控制面板，說明寫「交辦前」）。
2. 在右邊的 Chat（Local、Default permissions）貼上交辦的話，看一遍沒貼錯再送出：

> 照 lessons/2-1/expected.txt 的樣子，把 lessons/2-1/report.py 印出來的報表改成每一行對齊：金額加千分位逗號、靠右對齊。不要裝任何套件，只改 report.py。改完用 uv run 跑一次給我看。

3. 它要執行指令時會先問你（2026-11 的畫面：Run zsh command? 下面是那一行指令，按鈕是 **Allow**（同意）和 **Skip**（拒絕））。**一個一個看懂再按同意**；看不懂、或跟交辦的事無關（裝套件、刪檔、丟掉改動），就按 Skip，問它為什麼。
4. 看 diff：它改了哪幾行？只改了 report.py 嗎？看完按 Keep（Keep 只是「看過了、留著」，不會幫你按存檔點）。
5. 收下之前先跑檢查（`uv run check.py 2-1`），看報表那一題過了沒：印出來要跟 expected.txt 一模一樣。
6. 決定收不收，寫在 `decision.md`。收了，再按一個存檔點（說明寫「報表對齊」），最後再跑一次檢查，13 題都要過。不收，按 Undo，或回到交辦前的存檔點，改需求再交一次。

## 2. 提示

- **GitHub 是什麼：** 放程式碼的網站。這一課只開帳號、拿來登入 Copilot；把帳本放上 GitHub 是 3-3 的事，這一級不 push。
- **兩步驟驗證：** 登入時除了密碼，還要手機驗證 App 上一組會一直換的六位數。GitHub 官方建議用驗證 App（TOTP），比簡訊可靠。
- **noreply 信箱長什麼樣子：** 2017 年 7 月 18 日以後開的帳號是 `ID+帳號@users.noreply.github.com`（ID 是一串數字）。照抄 GitHub 頁面上給你的那一個，不要自己拼。
- **Copilot Free：** 官方方案頁寫 Copilot Free 的 agent 模式是 Included，每個月有一定的額度（AI credits），頁面沒有寫數字；用完了要等下個月，或改用聊天版。
- **它要執行的指令：** VS Code 會把 agent 要跑的那一行秀出來，旁邊有同意和拒絕。常見的唯讀指令可能直接跑；`rm` 這種有風險的指令一定會先問（VS Code 官方文件）。看懂了再按，看不懂就拒絕、問它。
- **Keep 不是存檔點：** VS Code 官方文件寫，agent 改的檔案已經存到磁碟上，Keep 只是「我看過了，留著」，不會幫你按存檔點。Undo、Restore Checkpoint 只還原它改的檔，**收不回終端機裡跑過的指令**。所以交辦前、收下後，都自己按存檔點。
- **一直按同意會麻木：** VS Code 官方文件也提醒，同意按多了，會越來越不仔細看。這一級「逐一按同意」是新手階段，第 5 級會改成事先寫好的規則。
- **`{amount:>5,}` 是什麼：** AI 交回來的寫法：`>5` 靠右、佔五格，`,` 加千分位逗號。讀得懂就好。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 2-1
```

它會把起點檔複製到你的帳本 `lessons/2-1/`：`report.py`、`expected.txt`、`commands.txt`、`decision.md`、`account.md`。

用 VS Code 打開帳本，在下面的終端機（帳本資料夾）先跑一次原本的報表：

```bash
uv run lessons/2-1/report.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 2-1
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 2-1`。）

## 4. 成品示範

```
$ uv run lessons/2-1/report.py
11 月月報
餐飲  1,250 元
交通    320 元
娛樂    480 元
其他     95 元
合計  2,145 元
$ git config --global user.email
一串數字+你的帳號@users.noreply.github.com
```

## 5. 怎麼測

`uv run check.py 2-1` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。

第一圈：`expected.txt` 要跟正確版一行一行、連空格都一樣，也要抓得到課程藏的 3 個「看起來對齊」的版本（金額靠左、少了千分位、合計那一行沒對齊）；git 的信箱是 noreply 信箱（先不開帳號的看 `account.md` 寫了沒）。第二圈：`commands.txt` 4 題。第三圈：存檔點裡有 report.py 原本的樣子（交辦前存過檔）、收下的版本也存進存檔點；`report.py` 印出來跟對齊的報表一模一樣（空格也算）；`decision.md` 五個標籤寫了沒。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| 第一圈「第 3 行不一樣」 | expected.txt 那一行的空格數目不對 | 數一數：最後一個數字要跟 1,250 的 0 對齊 |
| git 的信箱「現在是 bear@example.com」 | 還是 0-7 設的信箱 | 照第 1 節 B，複製 GitHub 給的 noreply 信箱再打一次 `git config --global user.email` |
| 存檔點裡找不到 report.py 原本的樣子 | 交給 AI 之前沒有先存檔 | 在原始碼控制面板放棄 report.py 的改動（Discard Changes）、按存檔點，再交辦一次 |
| `lessons/2-1/report.py 改過之後還沒按存檔點` | 收下了，可是還沒存 | 按 Keep 以後，再按一個存檔點 |
| report.py「第 6 行應該是『合計  2,145 元』」 | 合計那一行沒對齊 | 把 check 說的那一行貼回給 AI，請它照 expected.txt 改 |
| Chat 打不開、或要你先 Use AI Features | 還沒登入，或 AI 功能還是關著 | 照第 1 節 C 再做一次 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「2-1 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（開帳號與兩步驟驗證的官方步驟、Copilot Free 方案頁的原文、影片裡家教的完整對話、agent 實際要執行的指令與 diff）在 `補充.md`。
