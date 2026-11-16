# 1-22　錯誤處理：try／except／else／finally 與 raise

這課大約 45 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl；按 Control C 停下程式，Mac 和 Windows 都一樣（安裝見 0-W）。
要會的：def、return（1-18）、`from money import …`、`if __name__ == "__main__":`（1-21）、while True 加 break（1-10）、f-string（1-5）、assert（1-8）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 先猜（`predict.txt`）：3 題，先不要跑，用眼睛追 try、except、else、finally 會走哪幾段。

B. 讀 Traceback，再加上 raise（`money.py`）。起點檔的 `to_yuan` 就是 1-3 那台轉換機，1-3 你標了「# 已知會當掉」的國字「一百」，最下面那行會再試一次。先跑一次：

```bash
uv run lessons/1-22/money.py
```

印出 1200 以後跳出 Traceback。從最下面往上讀：最後一行是什麼錯（`ValueError`，'一百' 變不成整數）、往上一層是在哪一行丟出來的（第 4 行 `return int(text)`）、再往上是誰呼叫它（第 9 行）。

接著改 `to_yuan`：`return int(text)` 改成兩步，先 `amount = int(text)`；金額是負數時 `raise ValueError(f"金額不能是負數：{text}")`（訊息裡放進那個值）；不是負數才 `return amount`。看不懂的「一百」照樣讓 `int` 丟出 ValueError，**不要在 to_yuan 裡把它接住**：看不懂就說出來，接不接住交給呼叫它的人。

C. 亂輸入不再當掉（`add.py`）。用 `try` 包住 `amount = to_yuan(text)`：

- `except ValueError as e:` 印出「請再輸入一次。」和 `e`（錯誤訊息），迴圈再問一次；
- `else:`（try 裡沒出錯）印出「記下 120 元」這樣的一行，再 `break` 停下來。

**第②圈：AI 叫你用一個 except: 全部接住，問家教。** AI 給熊的建議長這樣（範例示意）：

```python
while True:
    try:
        text = input("金額：")
        amount = to_yuan(text)
        print("記下", amount, "元")
        break
    except:
        print("請再輸入一次")
```

這段在起點檔 `ai_bare.py` 裡，可以先跑跑看，在「金額：」後面按 Control C（停不下來就打 120 按 Enter）。照 `tutor.md` 的步驟拿去問家教（請它先問你問題，不要直接給答案），回答它、決定收不收，記在 `tutor.md`（四個標籤都寫了就算交了，內容不改對錯）。再做 `bare.txt` 3 題。

**第③圈：用 try 寫檢查（`checks_money.py`）。** 熊把 to_yuan 的要求寫成說明交給 AI：

| 輸入 | 應該 |
|---|---|
| `"1,200元"` 這種一般的金額 | 交回整數 1200 |
| `"一百"` 這種看不懂的 | 丟出 ValueError，訊息裡要有那段字 |
| `"-35"` 這種負數 | 丟出 ValueError，訊息裡要有那個值 |

課程藏了 3 個 AI 寫錯的版本（範例示意）。你的檢查（至少 3 條）要在正確版上全部成立、在每個寫錯的版本上至少有一條不成立。「應該丟出錯誤」的檢查用 try 寫，整段算一條：

```python
try:
    to_yuan("一百")
except ValueError as e:
    assert "一百" in str(e)
else:
    assert False
```

丟出 ValueError，就跳到 except，檢查訊息裡有沒有那段字；沒丟出錯誤，就走 else，`assert False` 讓這一條不成立。

## 2. 提示

- **Traceback 從下往上讀。** 第一行 `Traceback (most recent call last)` 是說「最後發生的寫在最下面」。最後一行是錯誤的種類和原因；往上每兩行一組：`File "…", line N, in 函式名`＋那一行程式。最上面那組是你一開始呼叫的地方，最下面那組是錯誤真正丟出來的地方。
- **try／except 怎麼走：** try 裡面的那幾行照順序跑；某一行丟出錯誤，**try 裡剩下的就跳過**，跳到種類對得上的 except；接住以後，程式從整段 try 的後面繼續跑。錯誤是在 try 裡呼叫的函式裡面丟出來的，也接得住。
- **except 只接寫明的那一種。** `except ValueError:` 只接 ValueError；別種錯（像文字加整數的 TypeError、打錯字的 NameError）接不到，照樣停下來、印出 Traceback——這是好事，bug 看得到。
- **`except ValueError as e`：** 把接住的錯誤取名叫 e，`print(e)` 或 `str(e)` 就是它的訊息。
- **else：** try 裡**沒出錯**才走。**finally：** 不管有沒有出錯都會走（常拿來收尾）。
- **raise：** 自己丟出一個錯誤。`raise ValueError("訊息")`：值不合理就丟 ValueError（官方文件：型別對、值不恰當），訊息寫清楚、放進那個值，看到錯誤就知道是哪一筆。
- **光禿禿的 except:（後面什麼都不寫）** 什麼錯都接住：打錯字的 NameError 被它接住，你只看到「請再輸入一次」，bug 被藏起來；按 Control C 想停下程式，丟出的 KeyboardInterrupt 也被它接住，程式停不下來。PEP 8（Python 的寫法建議）說：盡量寫明要接的錯，不要用光禿禿的 except。
- 程式停不下來時：按 Control C（Mac 和 Windows 都一樣）；光禿禿的 except 連它也接住的話，在終端機打一個它接受的金額讓迴圈結束，或直接關掉終端機分頁。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-22
```

它會把起點檔複製到你的帳本 `lessons/1-22/`：`predict.txt`、`money.py`、`add.py`、`ai_bare.py`（第②圈 AI 的建議，不檢查）、`bare.txt`、`tutor.md`、`checks_money.py`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-22/money.py
uv run lessons/1-22/add.py
uv run lessons/1-22/checks_money.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-22
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-22`。）

## 4. 成品示範

```
$ uv run lessons/1-22/add.py
金額：一百
請再輸入一次。 invalid literal for int() with base 10: '一百'
金額：-35
請再輸入一次。 金額不能是負數：-35
金額：120
記下 120 元
$ uv run lessons/1-22/checks_money.py
$
```

`checks_money.py` 什麼都沒印出來，代表每一條檢查都成立。

## 5. 怎麼測

`uv run check.py 1-22` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。第一圈：`predict.txt` 3 題、`money.py`（1,200元 還是 1200、-35 丟出 ValueError 而且訊息裡有 -35、一百照樣丟出 ValueError）、`add.py`（打一百、-35、120 不當掉、最後記下 120 元；第一次就打對直接記下；要寫明 except ValueError、不能用光禿禿的 except:）；第二圈：`bare.txt` 3 題、`tutor.md` 四個標籤寫了沒；第三圈：你的檢查抓不抓得到 3 個 AI 寫錯的版本、你的檢查在你的 money.py 上全部成立。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| 「to_yuan("-35") 應該丟出 ValueError，可是你的程式沒有丟出錯誤，交回了 -35」 | 還沒加負數的 raise | `amount = int(text)` 下面加 `if amount < 0:`、`raise ValueError(f"金額不能是負數：{text}")` |
| 「…有丟出 ValueError，可是錯誤訊息…裡沒有 -35」 | 訊息裡沒放那個值 | 用 f-string：`f"金額不能是負數：{text}"` |
| 「to_yuan("一百") 應該丟出 ValueError，…交回了 0」 | 在 to_yuan 裡把錯接住了 | 拿掉 to_yuan 裡的 try，讓 ValueError 丟出去 |
| 「不要用光禿禿的 except:」 | add.py 的 except 後面沒寫種類 | 寫成 `except ValueError as e:` |
| add.py 一直問、EOFError | 打對了沒有 break | `else:` 裡印完「記下」再 `break` |
| `SyntaxError: expected 'except' or 'finally' block` | try 後面沒有 except | try 下面那段的後面，接著寫 `except ValueError as e:` |
| 第三圈「壞版本 2 沒抓到」 | 你的檢查沒有負數那一條，或用了光禿禿的 except: | 加一條負數的 try，`except ValueError as e:` 寫明種類 |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-22 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教、聊天版 AI 的完整對話、Python 官方文件的原文、Traceback 每一行的意思）在 `補充.md`。
