# 2-6 第②圈：日圓換台幣（熊照 rate.py 改的，參數名字憑印象寫）
import httpx

URL = "https://api.frankfurter.dev/v2/rates"

r = httpx.get(URL, params={"base": "JPY", "symbols": "TWD"}, timeout=5)
r.raise_for_status()
print("1 日圓 =", r.json()[0]["rate"], "台幣")
