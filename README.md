# AI 時代的 Python 零基礎課：課程資料夾

這是 YouTube 頻道「不會寫程式 plusForm」的「AI 時代的 Python 零基礎課」課程資料夾，給完全沒寫過程式的人。
每一課都練三圈：第①圈自己寫、第②圈跟 AI 學、第③圈把事情交出去再驗收。這個資料夾放的是每一課的作業，和幫你檢查作業的程式。

> 目前是第一版骨架，只做好 4 課：0-4、0-5、0-C（Lv0 關卡）、1-9。其他課會陸續加進來。

## 你的電腦上會有兩個資料夾

兩個都放在 `~/code/` 底下。`~` 是你的「家目錄」，也就是你這個使用者自己的資料夾（Mac 上是 `/Users/你的名字`）。

| 資料夾 | 是什麼 | 你要改嗎 |
|---|---|---|
| `~/code/plusform-course/` | 課程資料夾，就是你現在看的這個 | 不要改，只讀 |
| `~/code/ledger/` | 你自己的帳本，作業都寫在這裡 | 要，這是你的 |

課程資料夾之後會整包更新（0-5 用 Download ZIP 下載，0-7 學會 git 以後改用 `git pull`）。你的作業和進度都放在帳本裡，所以更新課程不會蓋掉你的東西。

## 課程資料夾裡有什麼

| 名字 | 是什麼 |
|---|---|
| `check.py` | 檢查作業的程式。只用 Python 內建的功能，不會連上網、也不會呼叫任何 AI |
| `showcase/` | 課程準備的「agent 版帳本」示範（情境重現）：一支記帳程式，0-1 會看到它輸入「一百元」就當掉 |
| `concept_map.py` | 「看得懂進度條」：算出 showcase 那支程式你看得懂百分之幾 |
| `lessons/<課號>/` | 每一課一個資料夾，例如 `lessons/1-9/` |
| `course.json` | 整門課的課表順序 |
| `engine/` | check.py 用的零件，不用打開 |
| `tools/` | 老師用的工具 |
| `tests/` | 這個課程資料夾自己的自動測試 |

## 第一次使用（0-5 那一課會一步一步帶你做）

1. 照 0-5 裝好 uv。uv 是幫你管理 Python 的工具，這門課每一個指令都靠它。
2. 建好帳本資料夾，把它變成 uv 專案（0-4 已經建過資料夾的話，`mkdir -p` 不會蓋掉任何東西）：

   ```bash
   mkdir -p ~/code/ledger
   cd ~/code/ledger
   uv init --no-package --vcs none --python 3.13
   uv python pin 3.13
   uv run main.py
   ```

3. 下載課程資料夾（GitHub 頁面的 Download ZIP），解壓縮出來的 `plusform-course-main` 搬到 `~/code/`、改名成 `plusform-course`：

   ```bash
   mv ~/Downloads/plusform-course-main ~/code/plusform-course
   ```

4. 回到課程資料夾，告訴 check.py 你的帳本在哪裡（只要做一次）：

   ```bash
   cd ~/code/plusform-course
   uv run check.py setup ~/code/ledger
   ```

check.py 會把帳本的位置記在你電腦的設定檔裡（Mac 是 `~/.config/plusform-course/config.json`，Windows 是 `%APPDATA%\plusform-course\config.json`）。

## 每一課怎麼做

以 1-9 為例，都在課程資料夾裡打：

```bash
uv run check.py start 1-9   # 把這課的起點檔複製到你的帳本（已經有的檔案不會蓋掉）
# ……照 lessons/1-9/README.md 寫作業，作業檔在帳本的 lessons/1-9/ 裡……
uv run check.py 1-9         # 檢查
uv run check.py status      # 看進度、到期的回顧題、你猜得準不準、看得懂進度條
uv run check.py review      # 作答今天到期的回顧題
```

課號長得像 `0-4`、`0-5`、`1-9`。Lv0 關卡打 `lv0`（也可以打 `0-C`）；`env` 等於 `0-5`。

不在課程資料夾裡的時候，也可以打完整路徑：`uv run ~/code/plusform-course/check.py 1-9`。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `error: Failed to spawn: check.py`（後面還有 `No such file or directory`） | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course`；或用完整路徑 `uv run ~/code/plusform-course/check.py 1-9` |
| `check.py 要用 Python 3.13 跑` | 你打了 `python3 check.py` | 改打 `uv run check.py ……` |
| `還不知道你的帳本在哪裡` | 還沒做 setup | `uv run check.py setup ~/code/ledger` |
| `cd: no such file or directory: …/plusform-course` | 課程資料夾還沒搬到 `~/code/`，或名字還是 `plusform-course-main` | 照「第一次使用」第 3 步搬過去 |

## check.py 的五個固定習慣

1. **先猜再跑。** 每次檢查前，它會先問「這次一共 N 題，你覺得會過幾題？」並記下來。猜的跟實際差多少，會畫成「校準曲線」，在 `status` 裡看得到。差太多的時候，它會請你寫一句「下次我會怎麼估」。也可以在最後加 `--predict 數字` 直接告訴它。
2. **一次只看第一個錯。** 一開始只顯示第一個沒過的題目。先修好它再跑一次；想一次看全部，加 `--all`。
3. **太快全對會提醒。** 它會記下你打 `start`（或第一次跑檢查）的時間，跟第一次全部通過的時間。幾分鐘就全對，會跳出「這是警訊」：如果是 AI 幫你寫的，請關掉 AI 再寫一次第①圈。這只是提醒，不扣分。
4. **回顧題。** 你通過一課以後，往後第 2 課和第 5 課的檢查，會各帶一題這課的回顧題；每次最多問兩題，其他的排隊。跟上課**不同天**答對，技能樹才會長出一片葉子。
5. **兩種特殊作答。** 第③圈寫檢查時，如果某一條連正確版都會當掉，在那一行最後加 `# 已知會當掉`；如果你覺得是需求本身沒講清楚，加 `# 需求有問題`。標了以後，那一條就不套「正確版必須通過」的規則，改成對答案。

## 每一課的資料夾裡有什麼

| 名字 | 是什麼 |
|---|---|
| `README.md` | 這課的說明，固定六段：題目、提示、開始前要打的指令、成品示範、怎麼測、怎麼交 |
| `start/` | 起點檔。`uv run check.py start <課號>` 會把它複製到你帳本的 `lessons/<課號>/` |
| `tests/` | 官方測試（`checks.json`）。只測固定的檔名、函式名稱和固定的假資料 |
| `reference/` | **正確版**：課程凍結的正確寫法。第③圈拿它驗你寫的檢查：你的檢查在它上面要全部通過 |
| `mutants/` | **壞版本**：課程故意寫錯的 3 個版本。你的檢查在每一個壞版本上，至少要有一條不通過 |
| `answers/` | **對答用的固定答案**，還有第③圈的參考答案（老師也用它驗證壞版本） |
| `review/` | 回顧題 |
| `CONCEPTS.md` | 這課的示範、正確版和壞版本，只能用到哪些概念 |

為什麼正確版放 `reference/`、答案放 `answers/`？因為它們是兩種東西：`reference/` 是一支會跑的程式，check.py 拿它來驗你的檢查；`answers/` 是給人對的答案。

第③圈的「抓壞版本」：正確版像麥子、壞版本像穀殼，你寫的檢查要能把麥子留下、把穀殼篩掉。check.py 會用你看得懂的話回報，例如：「你的檢查抓到 2 個壞版本，還有 1 個溜過去：邊界 24」。

## 你的進度記在哪裡

全部寫在你的帳本 `~/code/ledger/.check/` 裡（前面有一個點的資料夾，平常會藏起來）：

| 檔案 | 記什麼 |
|---|---|
| `progress.json` | 每一課第一次跑、最後一次跑、第一次全過的時間，關卡的進度 |
| `attempts.jsonl` | 每次檢查的結果和你猜的分數（校準曲線用） |
| `reviews.jsonl` | 回顧題的作答 |
| `notes.jsonl` | 你寫的「下次我會怎麼估」 |

課程資料夾裡什麼都不寫。

## 費用

這門課免費：每一課都放在 YouTube，這個資料夾公開，不用註冊。
會花錢的只有工具：新手村到第三級用到的 VS Code、uv、Git、GitHub 都免費；0-8 起的 AI 聊天帳號用免費版就可以；第四級的 agent 工具（Claude Code、Codex）要付費方案，價格寫在那幾課的說明欄。這些錢是付給工具的公司，不是付給我們，課程裡也沒有推廣連結。

## Windows

Windows 一律用 Git Bash（裝 Git for Windows 就有）。指令跟 Mac 一樣。check.py 會自己把輸入餵給你的程式，所以 Mac 和 Windows 跑起來一樣。

## 要誠實講的事

YouTube 沒辦法監考，壞版本和檢查程式都放在這個公開的資料夾裡，想作弊一定作得到。所以這套檢查是拿來「校準自己」的，不發證書。

## 給老師

```bash
uv run tools/validate_lesson.py            # 驗證每一課：壞版本藏得住也抓得到、正確版全綠、起點檔沒問題、只用學過的概念
uv run concept_map.py --upto 1-27 --lines  # 看 showcase 每一行標了什麼概念
uv run tests/run_all.py                    # 跑這個資料夾自己的自動測試（不會碰到上層專案，也不寫 __pycache__）
uv run --no-project --python 3.13 python -B -m unittest discover -s tests -v   # 同上，另一種跑法
```

測試指令一定要加 `--no-project` 和 `-B`（或用 `tests/run_all.py`）：課程資料夾放在別的 uv 專案底下時，少了 `--no-project` 會把上層專案的 `.venv` 重建成 3.13；少了 `-B` 會在 `tests/` 底下寫出 `__pycache__`。

自動測試會建一個假的家目錄和假的帳本來跑完整流程。幾個只給測試用的環境變數：`PLUSFORM_CONFIG_DIR` 把設定檔換到假的家目錄、`PLUSFORM_NOW` 假裝是不同天、`PLUSFORM_PREDICT` 不用一題一題問預測、`PLUSFORM_TEST_WS` 指定測試檔要建在哪裡（沒設的話用系統的暫存資料夾）、`PLUSFORM_DEBUG=1` 讓 check.py 出意外時印出完整的錯誤訊息。測試也會檢查跑完之後課程資料夾裡一個檔案都沒多。

設計依據：每課 README 的六段照 CS50P 的作業格式；第③圈的抓壞版本是 Brown 大學 Examplar 的 wheat／chaff 做法（wheat 是正確版，chaff 是壞版本）。check.py 用 subprocess 把輸入餵給學員程式，不靠 shell 的 `<`；跑學員程式有時間上限和輸出上限，時間到會連子程序一起收掉；帳本的 uv 一律加 `--offline`，不讓它連網。
