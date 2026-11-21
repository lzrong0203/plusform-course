# 2-6　呼叫網路 API：狀態碼、逾時、假回應

這課大約 50 分鐘。三圈比例 45／30／25。Windows 同學：指令在 Git Bash 照打，⌘ 換成 Ctrl（安裝見 0-W）。
要會的：dict 與 list（1-13、1-15）、def 與 return（1-18）、import 與 `if __name__ == "__main__":`（1-21）、try／except（1-22）、with 與 Path（1-23）、uv add（2-2）、pytest（2-3：pytest.raises、tmp_path、monkeypatch）、JSON（2-4）、2-1 的交辦與核准（先存檔、指令看懂才按同意）。

帳本要支援外幣，就得知道今天的匯率。這一課用 **httpx**（一個幫 Python 上網拿資料的套件）去問一個匯率 **API**（給程式用的服務窗口：程式送出請求，它回一段資料）。
示範用的是 **Frankfurter**（frankfurter.dev）：不用金鑰、開放原始碼（MIT 授權），官方寫它的匯率可以免費用、會限流（rate-limited to prevent abuse）、也鼓勵把查到的結果存起來用。匯率每天會變，影片裡的數字是錄影那天的。
**測試和 check 都不打真網路**：用假回應（httpx 的 MockTransport）。

## 1. 題目

**第①圈：自己來（GET、狀態碼、逾時、假回應）。**

A. 先在帳本資料夾裝 httpx（2-2 學過）：

```bash
uv add httpx
```

B. 第一次呼叫（`rate.py`）。跑 `uv run lessons/2-6/rate.py`：

- 第 6 行 `httpx.get(URL, params=…, timeout=5)`：去問 API（GET 是「跟它要資料」），`params` 是附在網址後面的問題（base 是要換的錢、quotes 是要換成哪一種），`timeout=5` 是最多等五秒。
- 第 7 行印出 **狀態碼**：`200` 是成功。
- 第 8、9 行把回來的 **JSON** 讀成 Python 的 list（裡面一個 dict）印出來。

在「換你寫」那一行寫：

```python
print("1 美元 =", data[0]["rate"], "台幣")
```

C. 狀態碼（404）。把第 4 行的 `rates` 故意少打一個 `s`，再跑一次。第 7 行印出 `404`（找不到），但程式**沒有停**，跑到最後一行才出錯：`KeyError: 0`（404 回來的是一個 dict，不是 list）。httpx 拿到 404 不會自己喊停。
在第 6 行下面加一行：

```python
r.raise_for_status()
```

不是 2 開頭的狀態碼，它就當場丟出 `httpx.HTTPStatusError`，錯誤訊息直接寫著 `404 Not Found` 和網址（httpx 官方文件：raise an exception for any responses which are not a 2xx success code）。把 `s` 補回來。

D. 逾時。把 `timeout=5` 改成 `timeout=0.001`（千分之一秒）再跑：連線都還沒接上就超過時間，丟出 `httpx.ConnectTimeout`。看完改回 `timeout=5`。httpx 預設也是五秒（官方文件：raise a TimeoutException after 5 seconds of network inactivity）。

E. 假回應（`rates.py`、`tests/test_rates.py`）。`rates.py` 是課程準備的函式 `fetch_rate(client, base)`：連網路的 client 從外面交進來。測試的時候交一個**假的 client**：

```python
httpx.Client(transport=httpx.MockTransport(handler))
```

它要連網路時，改成問你寫的 `handler` 要回應（httpx 官方文件：return pre-determined responses, rather than making actual network requests）。想要 200、429（查太多次）、沒回應都做得出來，而且每次都一樣。課程準備的 `conftest.py` 會擋住真的網路：測試一打真網路就報錯。
在 `tests/test_rates.py` 補上 `test_429`：

```python
def test_429():
    def handler(request):
        return httpx.Response(429)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_rate(fake_client(handler), "USD")
```

跑 `uv run pytest lessons/2-6/tests/test_rates.py`：2 passed。再答 `api.txt` 3 題。

**第②圈：跟 AI 學（`jpy.py`、`codes.txt`、`docs.md`）。** 熊照 rate.py 改了一份日圓換台幣的 `jpy.py`，參數名字憑印象寫成 `symbols`。跑 `uv run lessons/2-6/jpy.py`：`422 Unprocessable Entity`。
請家教幫忙，它不會直接給答案，會帶你去查**官方文件**：Frankfurter 寫的是 `Filter target currencies with quotes`，錯誤那一段寫 `422 Request understood but cannot be processed`。改成 `"quotes": "TWD"` 再跑。答 `codes.txt` 3 題，寫 `docs.md`（五個標籤都寫了就算交了）。

**第③圈：先寫驗收，再交給 AI。**

1. 打開 `tests/test_cache.py`：`ok_client` 是會回答 32.5 的假服務（還會記下被問了幾次）、`down_client` 是掛掉的假服務（等不到回應）。`test_cache_one_hour` 已經寫好（一小時內不再問）。在 `test_api_down` 最後補兩行：

```python
    assert rate == 32.5
    assert "上一次" in note
```

跑 `uv run pytest lessons/2-6`：還沒有 rate_cache.py，先紅（ModuleNotFoundError）。

2. 到原始碼控制面板按存檔點，說明寫「交辦前」。

3. 在 Copilot Chat 選 Agent，貼上這四欄（沒開 GitHub 帳號：用聊天版 AI 寫好再貼上，或打 `cp lessons/2-6/ai_rate_cache.py lessons/2-6/rate_cache.py`）：

```
目標：寫 lessons/2-6/rate_cache.py 的 cached_rate(client, base, now, cache_file)，交回 (匯率, 提示)。
背景：匯率用 rates.py 的 fetch_rate(client, base) 查；查到的存在 cache_file（JSON），記下查的時間。
限制：一小時內查過就用存著的，不再問 API；API 掛掉時交回上一次的值，提示裡寫「上一次」；不能改 tests/、不能裝套件；它要執行的指令先給我看。
怎樣算做完：uv run pytest lessons/2-6 全部通過，附上輸出。
```

4. 它要執行的指令看懂才按同意。跑 `uv run pytest lessons/2-6` 驗收。課程凍結的 AI 版本（`ai_rate_cache.py`）自己跑印得出匯率，但 `test_api_down` 會紅：它只接住 `httpx.HTTPStatusError`（狀態碼不對），API 沒回應是 `ConnectTimeout`，沒接住就整個當掉。改成 `except httpx.HTTPError:`（兩種的上一層），改到全過。
5. 寫 `decision.md`，收了再按一個存檔點。

## 2. 提示

- **先看狀態碼：** 2 開頭成功；4 開頭多半是我們送過去的有問題（404 找不到、422 參數不對、429 查太多次）；5 開頭是伺服器那邊的問題。`r.raise_for_status()` 讓不是 2 開頭的當場報錯。
- **一定設 timeout：** 網路那頭可能不回。超過時間丟出 `httpx.TimeoutException`（`ConnectTimeout`、`ReadTimeout` 都是它底下的）。
- **兩種出錯：** 沒回應、連不上是 `httpx.RequestError`；狀態碼不對是 `httpx.HTTPStatusError`；兩種的上一層是 `httpx.HTTPError`。
- **參數名字查官方文件：** 每個 API 自己定，不要憑印象。
- **測試不打真網路：** 用 `httpx.MockTransport` 做假回應；`conftest.py` 會擋住真的連線。
- **不要狂查別人的服務：** 查到的匯率存起來用（第③圈的快取），一小時內不再問。
- **第 2 級交辦給 agent 的三條規矩：** 它不能改 `tests/`、不能用 pip 裝套件、沒附測試的輸出不算做完。

## 3. 開始前要打的指令

```bash
cd ~/code/plusform-course
git pull
uv run check.py start 2-6
```

它會把起點檔複製到你的帳本 `lessons/2-6/`：`rate.py`、`jpy.py`、`rates.py`、`conftest.py`、`tests/test_rates.py`、`tests/test_cache.py`、`ai_rate_cache.py`、`api.txt`、`codes.txt`、`docs.md`、`decision.md`。

用 VS Code 打開帳本，在下面的終端機（帳本資料夾）打第 1 節的指令，例如：

```bash
uv add httpx
uv run lessons/2-6/rate.py
uv run lessons/2-6/jpy.py
uv run pytest lessons/2-6
```

檢查的時候**回到課程資料夾**：

```bash
cd ~/code/plusform-course
uv run check.py 2-6
```

## 4. 成品示範

```
$ uv run lessons/2-6/rate.py
200
[{'date': '2026-11-20', 'base': 'USD', 'quote': 'TWD', 'rate': 32.985}]
1 美元 = 32.985 台幣
$ uv run pytest lessons/2-6
4 passed
```

（匯率每天不一樣，你跑出來的數字會不同。）

## 5. 怎麼測

`uv run check.py 2-6` 會先問你：「你覺得會過幾題？」先猜一個數字再按 Enter，它才開始檢查。**check 不打真網路**：rate.py、jpy.py 用假回應跑（把 httpx 真的連線換掉），測試都在系統的暫存資料夾裡跑。

第一圈：httpx 裝好了、rate.py（印出匯率、404 當場報錯、timeout 改回來）、test_rates.py（抓到兩個壞版本）、api.txt 3 題；第二圈：jpy.py（參數名字對了）、codes.txt 3 題、docs.md；第三圈：你的 test_cache.py 在正確版上全過、抓得到四個壞版本（沒回應就當掉、沒用上一次的值、沒有提示、快取太短）；你的 rate_cache.py 遇到另一組情況（503、429、連不上）也對；交辦前先存檔、decision.md。

沒過的，它只先告訴你第一個沒過的，修好再跑一次（想一次看全部，最後加 `--all`）。

### 常見錯誤

| 你看到 | 意思 | 怎麼辦 |
|---|---|---|
| `ModuleNotFoundError: No module named 'httpx'` | 帳本還沒裝 httpx | 在帳本資料夾打 `uv add httpx` |
| `KeyError: 0` | 回來的不是 list（多半是狀態碼不是 200） | 先加 `r.raise_for_status()`，看狀態碼 |
| `httpx.HTTPStatusError: Client error '404 Not Found'` | 網址打錯了 | 對照官方文件的網址 |
| `httpx.HTTPStatusError: Client error '422 Unprocessable Entity'` | 參數它不認得 | 查官方文件的參數名字 |
| `httpx.HTTPStatusError: Client error '429 Too Many Requests'` | 查太多次 | 等一下再查；查到的存起來用 |
| `httpx.ConnectTimeout` | 超過 timeout 還沒連上 | 檢查網路；timeout 不要設太短 |
| `RuntimeError: 測試打了真網路` | 測試沒有用假的 client | 交 `fake_client(handler)` 進去，不要在函式裡自己開 httpx.Client |
| `error: Failed to spawn: check.py` | 你不在課程資料夾裡 | 先打 `cd ~/code/plusform-course` |

## 6. 怎麼交

check 全對就算這課過了，它會記在你帳本的 `.check/` 裡，不用上傳。在 VS Code 按一個存檔點（說明寫「2-6 完成」）。

技能樹上這課的葉子，要過兩課以後、改天答對回顧題才會長出來。下一課是 2-7〈金鑰與環境變數〉。
