# 2-6 第①圈：呼叫匯率 API（Frankfurter：不用金鑰）
import httpx

URL = "https://api.frankfurter.dev/v2/rates"

r = httpx.get(URL, params={"base": "USD", "quotes": "TWD"}, timeout=5)
print(r.status_code)
data = r.json()
print(data)
# 換你寫：印出「1 美元 = ○○ 台幣」
