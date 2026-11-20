# 2-5　SQLite 與 SQL 基礎

這課大約 50 分鐘。三圈比例 45／30／25。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：dict（1-15）、for（1-11）、def 與 return（1-18）、import（1-21）、with open 與 Path（1-23）、class 的方法（1-24）、pytest（2-3）、csv.DictReader（2-4）、2-1 的交辦與核准（先存檔、指令看懂才按同意）。

帳越記越多，每次想知道「這個月餐飲花了多少」，都要再寫一個新的迴圈。這一課把帳放進一個 **SQLite** 資料庫（一個檔案就是一個資料庫，Python 內建 `sqlite3` 模組，不用裝），再用 **SQL**（跟資料庫說「我要哪些資料」的語言）一行問出來。
這裡做的 `practice.db` 只是練習檔：帳本正式搬進資料庫在 5-5。`entries.csv` 是課程編的假資料。

## 1. 題目

**第①圈：自己來（建表、放進去、查出來）。**

A. 先看 CSV 版的答案。在帳本資料夾跑：

```bash
uv run lessons/2-5/csv_totals.py
```

印出 11 月各分類的合計（餐飲 635、交通 500、日用品 680、娛樂 320）。這是 2-4 學過的寫法：一筆一筆讀、用 dict 加起來。等一下用 SQL 查出同樣的數字。

B. 建資料表（`import_csv.py`）。在「換你寫」那一行寫：

```python
con.execute("CREATE TABLE entries (date TEXT, item TEXT, category TEXT, amount INTEGER, note TEXT)")
```

資料表（table）像一張試算表：`entries` 是表的名字，括號裡是五個欄位，`TEXT` 是文字、`INTEGER` 是整數。

C. 存檔，跑一次 `uv run lessons/2-5/import_csv.py`。它用 f-string 把每一筆組成一句 `INSERT INTO entries VALUES (…)`，印出來再交給資料庫。印到第 9 筆就當掉：

```
INSERT INTO entries VALUES ('2026-11-15', '麵包店', '餐飲', 450, '熊's 生日蛋糕')
sqlite3.OperationalError: near "s": syntax error
```

備註裡的單引號，把 `'熊'` 提早收掉了，後面的 `s 生日蛋糕'` 被當成 SQL 的一部分。**資料變成了指令的一部分**：要是有人故意在備註寫一段 SQL，就能改掉這句指令要做的事，這叫 **SQL 注入**（SQL injection）。

D. 改成用問號交值。把 `sql = …`、`print(sql)`、`con.execute(sql)` 三行換成：

```python
        con.execute("INSERT INTO entries VALUES (?, ?, ?, ?, ?)", (d, item, cat, amount, note))
```

SQL 裡只留五個問號，值用一個 tuple 另外交給 `execute`，sqlite3 會把它們原樣存成資料，單引號不會被當成指令（Python 官方文件：use the DB-API's parameter substitution）。金額空白的 `None` 也會存成 SQL 的 **NULL**（沒有值）。再跑一次：`一共 11 筆`。

E. 查詢（`q1.sql`、`q2.sql`）。課程準備了一個小工具 `run_sql.py`，把 .sql 檔交給 practice.db 跑、印出查到的每一列：

```bash
uv run lessons/2-5/run_sql.py q1.sql
```

- `q1.sql`：列出餐飲這一類的每一筆。`SELECT` 拿哪幾欄、`FROM` 哪一張表、`WHERE` 挑出哪幾筆：

```sql
SELECT date, item, amount, note FROM entries WHERE category = '餐飲';
```

SQL 裡的文字用單引號包起來，最後一個分號。熊's 生日蛋糕的備註照原樣存著。

- `q2.sql`：本月各分類的合計。`LIKE '2026-11%'` 是「2026-11 開頭的都算」（`%` 代表後面接什麼都可以）；`GROUP BY category` 把分類一樣的分成一組，`SUM(amount)` 把每一組加起來：

```sql
SELECT category, SUM(amount) FROM entries
WHERE date LIKE '2026-11%'
GROUP BY category;
```

跑出來會多一列 `醫療 | None`：牙醫那一筆的金額是空的（NULL），SUM 只加有值的，一個都沒有就是 NULL，Python 讀出來是 None。CSV 版跳過了金額空白的，所以要在 WHERE 加上 `AND amount IS NOT NULL`（NULL 要用 `IS` 比，不能用 `=`）。四個數字就跟 CSV 版一樣了。

- `sql.txt` 3 題。

**第②圈：跟 AI 學（`tiny.sql`、`null.txt`、`verify.md`）。** 請家教解釋這一條 SQL 在做什麼：

```sql
SELECT category, COUNT(*), COUNT(amount), AVG(amount)
FROM t GROUP BY category;
```

不要只聽它說：用 **5 筆小資料**自己跑一次（`tiny.sql`：故意放一筆金額空白的，先自己算答案再跑），對照它的解釋。`uv run lessons/2-5/run_sql.py tiny.sql`（這個檔自己建一張小表，跑在用完就丟的空資料庫，不動 practice.db）。再答 `null.txt` 3 題，寫 `verify.md`（五個標籤都寫了就算交了）。

**第③圈：先寫驗收，再交給 AI。**

1. 在 `tests/test_db.py` 寫 `test_totals`：11 月各分類的合計應該是多少？**自己手算**，要跟 CSV 版一樣（客運退票是負的，要扣掉；金額空白的不算）：

```python
def test_totals():
    totals = category_totals(make_db(), "2026-11")
    assert totals == {"餐飲": …, "交通": …, "日用品": …, "娛樂": …}
```

跑 `uv run pytest lessons/2-5`：還沒有 db_report.py，先紅（ModuleNotFoundError）。

2. 到原始碼控制面板按存檔點，說明寫「交辦前」（2-1 學過：交給 AI 之前先存檔）。

3. 在 Copilot Chat 選 Agent，貼上這四欄（沒開 GitHub 帳號：用聊天版 AI 寫好再貼上，或打 `cp lessons/2-5/ai_db_report.py lessons/2-5/db_report.py`）：

```
目標：寫 lessons/2-5/db_report.py 的 category_totals(con, month)，查某個月（例如 "2026-11"）各分類的合計，交回 {分類: 合計}。
背景：con 是 sqlite3 的連線，資料表 entries 有 date、item、category、amount、note 五欄（ledger_db.py 的 load_csv 放的）。金額空白的存成 NULL，退票是負的。
限制：只用內建的 sqlite3，值用問號交給 execute；不能改 tests/、不能裝套件；它要執行的指令先給我看。
怎樣算做完：合計跟 CSV 版（csv_totals.py）算出來的一樣；uv run pytest lessons/2-5 全部通過，附上輸出。
```

4. 它要執行的指令看懂才按同意。跑 `uv run pytest lessons/2-5` 驗收。課程凍結的 AI 版本（`ai_db_report.py`）會錯在 `交通`：它想跳過金額空白的，寫了 `amount > 0`，退票是負的，也被跳過了。改成 `amount IS NOT NULL`，改到全過。
5. 寫 `decision.md`，收了再按一個存檔點。

## 2. 提示

- **SQLite 是一個檔案：** `sqlite3.connect("practice.db")` 打開（沒有就建一個新的）；改了資料要 `con.commit()` 才會存進檔案。`":memory:"` 是只在記憶體裡、用完就丟的資料庫（測試用）。
- **SQL 的四個字：** `SELECT` 拿哪幾欄、`FROM` 哪一張表、`WHERE` 挑出哪幾筆、`GROUP BY` 照什麼分組。大小寫都可以，習慣上關鍵字寫大寫。
- **值一律用問號交：** 不要用 f-string 或 `+` 把值拼進 SQL。單引號、奇怪的備註、有人故意寫的一段 SQL，都會變成指令的一部分。
- **NULL：** 沒有值。`SUM`、`AVG`、`COUNT(amount)` 都會跳過 NULL；`COUNT(*)` 數的是列數，NULL 那一列也算。要挑出空白的用 `amount IS NULL`，跳過空白的用 `amount IS NOT NULL`。
- **amount > 0 不等於跳過空白：** 它也會跳過負的（退款、退票）。
- **第 2 級交辦給 agent 的三條規矩：** 它不能改 `tests/`、不能用 pip 裝套件、沒附測試的輸出不算做完。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 2-5
```

它會把起點檔複製到你的帳本 `lessons/2-5/`：`entries.csv`（假資料）、`csv_totals.py`、`import_csv.py`、`run_sql.py`、`q1.sql`、`q2.sql`、`sql.txt`、`tiny.sql`、`null.txt`、`verify.md`、`ledger_db.py`、`conftest.py`、`tests/test_db.py`、`ai_db_report.py`、`decision.md`。

用 VS Code 打開帳本，在下面的終端機（帳本資料夾）打第 1 節的指令，例如：

```bash
uv run lessons/2-5/csv_totals.py
uv run lessons/2-5/import_csv.py
uv run lessons/2-5/run_sql.py q1.sql
uv run lessons/2-5/run_sql.py q2.sql
uv run lessons/2-5/run_sql.py tiny.sql
uv run pytest lessons/2-5
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 2-5
```

## 4. 成品示範

```
$ uv run lessons/2-5/import_csv.py
一共 11 筆
$ uv run lessons/2-5/run_sql.py q2.sql
category | SUM(amount)
交通 | 500
娛樂 | 320
日用品 | 680
餐飲 | 635
$ uv run lessons/2-5/run_sql.py tiny.sql
category | COUNT(*) | COUNT(amount) | AVG(amount)
交通 | 3 | 2 | 45.0
餐飲 | 2 | 2 | 150.0
```

## 5. 怎麼測

`uv run check.py 2-5` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。check 在系統的暫存資料夾裡跑你的程式和 SQL，不會動你帳本裡的 practice.db。

第一圈：import_csv.py 建的表（五欄、11 筆、熊's 生日蛋糕照原樣、牙醫的金額是 NULL）、q1.sql、q2.sql（跟 CSV 版一樣）、sql.txt 3 題；第二圈：tiny.sql（5 筆、一筆金額空白）、null.txt 3 題、verify.md；第三圈：你的 test_db.py 在正確版上全過、抓得到三個壞版本（漏掉退票、把 NULL 當 0、沒篩月份）；你的 db_report.py 查一份你沒看過的帳；交辦前先存檔、decision.md。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `sqlite3.OperationalError: near "s": syntax error` | 備註的單引號被當成 SQL 的一部分 | 值用問號交給 execute |
| `sqlite3.OperationalError: no such table: entries` | 還沒建表（或 CREATE TABLE 寫在 INSERT 後面） | 先寫 CREATE TABLE |
| `sqlite3.OperationalError: table entries already exists` | 同一個檔建了兩次表 | import_csv.py 開頭的 unlink 不要刪 |
| `no such column: None` | 金額空白的 None 被 f-string 拼成字 None | 用問號交值，None 會存成 NULL |
| q2 多一列 `醫療 \| None` | 醫療只有一筆，金額是 NULL | WHERE 加 `AND amount IS NOT NULL` |
| pytest：`'交通': 920` 不等於 `500` | 退票被跳過了（`amount > 0`） | 改成 `amount IS NOT NULL` |
| `還沒有 practice.db` | 還沒跑 import_csv.py | 先跑 `uv run lessons/2-5/import_csv.py` |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「2-5 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。下一支是檢核站 2-C1（關掉 AI，30 分鐘），會考寫 1 條 GROUP BY。
