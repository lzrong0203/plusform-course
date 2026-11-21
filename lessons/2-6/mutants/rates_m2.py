# 壞版本 m2：狀態碼不是 200 就悄悄交回 None，不報錯
import httpx

URL = "https://api.frankfurter.dev/v2/rates"


def fetch_rate(client, base):
    """查 1 單位的 base（例如 "USD"）等於多少台幣。client 從外面交進來，測試時換成假的。"""
    r = client.get(URL, params={"base": base, "quotes": "TWD"}, timeout=5)
    if r.status_code != 200:
        return None
    return r.json()[0]["rate"]
