# 1-24　類別與物件：Entry、Ledger、@dataclass

這課大約 45 分鐘。三圈比例 60／25／15。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：tuple（1-14）、dict（1-15）、可變與參照（1-16）、def、return、docstring（1-18）、預設參數的陷阱（1-19）、型別提示（1-20）、import（1-21）。

## 1. 題目

**第①圈：自己寫（關掉 AI）。**

A. 先猜（`predict.txt`）：3 題，先不要跑。少給一個欄位會怎樣、沒有 `@dataclass` 的 `==`、兩個物件各有各的屬性。

B. 一筆帳寫成物件（`entry.py`）。起點檔最下面已經寫好幾行 print。在註解下面寫：

```python
@dataclass
class Entry:
    date: str
    item: str
    amount: int
```

- `class Entry:`：自己定義一種資料，名字叫 Entry。這一段是**類別**：規定每一筆帳要有哪些欄位，像模具，它本身還不是一筆帳。
- 下面三行是欄位：`date`、`item`、`amount`。冒號後面的 `str`、`int`（1-20 的型別提示）說它放文字還是整數。
- `@dataclass`：寫在 class 上面一行，會幫這個類別自動補上 `__init__`（做物件時要給哪些值）、印出來好看的樣子（`__repr__`）、比每個欄位的 `==`（`__eq__`）。

寫好以後，`Entry("11/03", "午餐", 120)` 就照順序放進日期、項目、金額，做出一筆帳：這一筆叫做**物件**。`lunch.amount` 拿到它的金額：點後面接的名字叫做**屬性**。跑起來要印出：

```
Entry(date='11/03', item='午餐', amount=120)
公車 15
135
```

**第②圈：跟家教一起寫 Ledger（`ledger.py`、`tutor.md`）。** 用 0-8 的「帶我寫」：每一步你先說要做什麼、你先寫，家教再說對不對，不要它直接給整段程式（步驟在 `tutor.md`）。Ledger 要有：

- 每本帳本自己的 `entries`（一開始是空的 list）；
- `add(self, entry)`：把一筆 Entry 放進 `entries` 最後面；
- `total(self)`：交回所有金額的合計，沒有帳交回 0。

起點檔最下面做了兩本帳本 nov 和 dec，只在 nov 加兩筆，要印出 `2 0` 和 `135 0`（dec 還是空的）。

**第③圈：需求寫進 docstring，交給 AI，再驗收。** 熊想在 Ledger 加一個 `biggest()`，docstring 寫：

> 交回金額最大的那一筆 Entry；帳本是空的，交回 None。

`ledger_ai.py` 是 AI 交回來的版本（課程準備的固定版本，範例示意，不要改它）。

1. 在 `checks_ledger.py` 寫 assert 驗收 biggest（至少 3 條）。你的檢查要在正確的版本上全部成立、在課程藏的 3 個 AI 寫錯的版本上至少有一條不成立。想想 AI 最容易寫錯哪裡：空的帳本？最大的那一筆不在最前面、也不在最後面？
2. 你的檢查跑 `ledger_ai.py` 會全部成立。可是打開它從頭讀一遍：需求只有 biggest，它卻多寫了 `BaseLedger`、`MonthlyLedger`、`FoodLedger` 三個類別。在 `review.txt` 回答 3 題：收不收、`class MonthlyLedger(Ledger):` 是什麼意思、多做的 `MonthlyLedger` 藏了什麼行為。

## 2. 提示

- **類別和物件：** `class Entry:` 那一段是類別（模具），`Entry("11/03", "午餐", 120)` 做出來的是物件（一筆一筆的帳）。同一個類別可以做出很多個物件，**各有各的屬性**：改 `bus.amount`，`lunch.amount` 不會跟著變。
- **少給一個欄位：** dict 少一個鍵照樣收下，要等用到那個鍵才 `KeyError`；`@dataclass` 的 Entry 少給一個值，做物件那一行就 `TypeError: Entry.__init__() missing 1 required positional argument: 'amount'`。
- **`__init__` 和 self：** 沒有 `@dataclass` 時，AI 常寫成：

```python
class Entry:
    def __init__(self, date, item, amount):
        self.date = date
        self.item = item
        self.amount = amount
```

  `__init__` 是做物件的時候 Python 自動跑的函式；第一個參數 `self` 就是正在做的那一個物件，`self.date = date` 把日期存進它。呼叫方法時，**點前面的那一個物件會交給 self**：`nov.add(e)` 裡的 self 就是 nov（官方教學：`x.f()` 跟 `MyClass.f(x)` 一樣）。`self` 只是大家約好的名字（官方教學：nothing more than a convention），還是一律寫 self。
- **沒有 `@dataclass` 的 `==`：** 比的是「是不是同一個物件」（像 1-16 的 `is`），兩筆一模一樣的帳也是 False；`@dataclass` 會幫你寫比每個欄位的 `==`。
- **list 不要寫在 class 下面：** 

```python
class Ledger:
    entries = []          # 寫在這裡，每本帳本共用同一個 list
```

  nov 加一筆，dec 也看得到（官方教學 9.3.5 的 tricks 例子）。要每本各一個，在 `def __init__(self):` 裡面寫 `self.entries = []`。用 `@dataclass` 寫帳本的話，`entries: list = []` 會直接 `ValueError`，要寫 `entries: list = field(default_factory=list)`（`from dataclasses import dataclass, field`）：跟 1-19 預設參數用空的 list 是同一個坑。
- **繼承（看得懂就好）：** `class Ledger(BaseLedger):` 是說 Ledger 是一種 BaseLedger：自己沒寫的方法，往上一層找（官方教學 9.5）；自己寫了同名的方法，就蓋掉上一層的。`super().add(entry)` 是「叫上一層的 add」。
- **什麼時候 dict 就夠了：** 欄位固定、很多地方都要用、還想附上自己的動作（add、total），值得寫成類別；只在一兩個地方用、或是每筆想記的欄位不一樣，dict 加函式就夠了。兩種寫法都對，挑讀起來最清楚的那一個。
- **多做的也不收：** 測試只證明需求那一部分是對的。需求沒要的類別，多一個就多一份要讀、要測、可能藏錯的程式。少做不收、做錯不收，多做了沒要求的，也不收：退回去，請它只照 docstring 寫。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 1-24
```

它會把起點檔複製到你的帳本 `lessons/1-24/`：`predict.txt`、`entry.py`、`ledger.py`、`tutor.md`、`ledger_ai.py`（AI 交回的版本，不要改）、`checks_ledger.py`、`review.txt`。

用 VS Code 打開帳本，寫完存檔，在 VS Code 下面的終端機（帳本資料夾）自己跑跑看：

```bash
uv run lessons/1-24/entry.py
uv run lessons/1-24/ledger.py
uv run lessons/1-24/checks_ledger.py
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 1-24
```

（也可以不切資料夾，直接打完整路徑：`uv run ~/code/plusform-course/check.py 1-24`。）

## 4. 成品示範

```
$ uv run lessons/1-24/entry.py
Entry(date='11/03', item='午餐', amount=120)
公車 15
135
$ uv run lessons/1-24/ledger.py
2 0
135 0
$ uv run lessons/1-24/checks_ledger.py
$
```

`checks_ledger.py` 什麼都沒印，就是每一條 assert 都成立。

## 5. 怎麼測

`uv run check.py 1-24` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。

第一圈：`predict.txt` 3 題、`entry.py` 跑起來印出三行、**Entry 的欄位與相等比較**（check 用課程準備的小程式載入你的 entry.py，另外做一筆 12/01 書 450：屬性、印出來的樣子、一樣的兩筆 `==` 是 True、金額不一樣是 False、少給金額要跳出 TypeError）；第二圈：`ledger.py` 印出 `2 0` 和 `135 0`、**Ledger.add 與加總**（另外做兩本帳本 a、b：a 加兩筆、b 還是 0 筆，total 算對，空的帳本是 0）、`tutor.md` 四個標籤寫了沒；第三圈：你的檢查抓不抓得到 3 個 AI 寫錯的 biggest、`review.txt` 3 題。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。不到 8 分鐘就全對，它會印出提醒：只是提醒，不扣分。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `NameError: name 'Entry' is not defined` | 還沒寫 class Entry，或名字打錯 | 在註解下面寫 `@dataclass` 和 `class Entry:` |
| `NameError: name 'dataclass' is not defined` | 最上面那行 import 被刪掉了 | 留著 `from dataclasses import dataclass` |
| 印出 `<__main__.Entry object at 0x…>` | class 上面少了 `@dataclass` | 在 `class Entry:` 上面一行加 `@dataclass` |
| `TypeError: Entry() takes no arguments` | 少了 `@dataclass`，也沒寫 `__init__` | 加上 `@dataclass` |
| `IndentationError` | 三個欄位沒有空四格 | `date: str` 這三行前面空四格 |
| 印出 `2 2` | entries 寫在 class 下面，兩本帳本共用 | 改到 `def __init__(self):` 裡：`self.entries = []` |
| `TypeError: Ledger.add() takes 1 positional argument but 2 were given` | `def add(entry):` 少了 self | 寫成 `def add(self, entry):` |
| `NameError: name 'entries' is not defined` | 方法裡寫 `entries.append(…)` | 要寫 `self.entries.append(…)` |
| `ValueError: mutable default <class 'list'> for field entries is not allowed` | `@dataclass` 的欄位寫了 `= []` | 改成 `field(default_factory=list)` |
| 第三圈「壞版本 2 沒抓到」 | 你的檢查沒有空的帳本 | 寫一條：還沒 add 的帳本，`biggest()` 是 None |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「1-24 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。補充說明（影片裡熊和家教的完整對話、Python 官方文件的原文、自評兩題：畫物件圖、用三句話說明 self）在 `補充.md`。
