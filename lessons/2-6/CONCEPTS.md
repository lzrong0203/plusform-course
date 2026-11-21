# 2-6 用到的概念

這課的示範、起點檔、正確版（`reference/`）、壞版本、參考答案，只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 2-6 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 數字運算（`now - datetime.fromisoformat(...)`）
- 資料型別（`None`）
- 字串操作（f-string、`isoformat`）
- 函式呼叫
- 比較與邏輯（`<`、`and`、assert、`in`）
- if
- for
- list（`data[0]`、`calls.append`、`len(calls)`）
- tuple 與 set（交回 `(匯率, 提示)`）
- dict（`params={...}`、`cache.get(base)`、`old["rate"]`）
- 函式定義（函式裡面再定義一個 handler：測試的假回應）
- 預設值與關鍵字參數（`params=`、`timeout=`、`transport=`、`encoding=`、`ensure_ascii=False`、`timespec=`）
- 模組與 import（`datetime`、`timedelta`、`from rates import fetch_rate`、`if __name__ == "__main__":`）
- 例外處理（try／except、`raise`、`except httpx.HTTPError`）
- 檔案讀寫（`Path`、`read_text`、`write_text`、`exists`、`with`）
- class（`httpx.Client(...)`、`r.json()`、`r.raise_for_status()` 這種物件和它的方法：1-24 教過）
- CSV 與 JSON（`json.loads`、`json.dumps`）
- 呼叫網路 API（httpx：`get`、`params`、`timeout`、狀態碼、`raise_for_status`、`json`、`Client`、`MockTransport`、`Response`、`HTTPError`、`HTTPStatusError`、`ConnectTimeout`）

`*.txt` 是對答，`docs.md`、`decision.md` 是自評的表單，都不在檢查範圍。
`conftest.py` 是課程準備的（擋住真的網路、讓 pytest 找得到同一個資料夾的 rates.py），`rates.py` 是課程準備的函式，不用改。
`probe/` 是 check 用的小程式（學員不用看）。測試的 `@pytest.fixture`、`pytest.raises`、`tmp_path`、`monkeypatch` 是 2-3 教過的 pytest 寫法。
