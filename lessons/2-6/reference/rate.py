# 2-6 第①圈：呼叫匯率 API（Frankfurter：不用金鑰）
import httpx

URL = "https://api.frankfurter.dev/v2/rates"

r = httpx.get(URL, params={"base": "USD", "quotes": "TWD"}, timeout=5)
r.raise_for_status()
print(r.status_code)
data = r.json()
print(data)
print("1 美元 =", data[0]["rate"], "台幣")
