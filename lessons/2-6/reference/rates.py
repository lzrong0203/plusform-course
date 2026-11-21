# 2-6：查匯率的函式（課程準備：第①圈的測試、第③圈的快取都會用到）
import httpx

URL = "https://api.frankfurter.dev/v2/rates"


def fetch_rate(client, base):
    """查 1 單位的 base（例如 "USD"）等於多少台幣。client 從外面交進來，測試時換成假的。"""
    r = client.get(URL, params={"base": base, "quotes": "TWD"}, timeout=5)
    r.raise_for_status()
    return r.json()[0]["rate"]
