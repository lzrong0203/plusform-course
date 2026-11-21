# 壞版本 m3：API 掛掉時用了上一次的值，但沒有提示
import json
from datetime import datetime, timedelta
from pathlib import Path

import httpx

from rates import fetch_rate


def cached_rate(client, base, now, cache_file):
    """回傳 (匯率, 提示)。一小時內查過就用快取；API 掛掉時用上一次的值，提示裡寫「上一次」。"""
    cache = json.loads(cache_file.read_text(encoding="utf-8")) if cache_file.exists() else {}
    old = cache.get(base)
    if old and now - datetime.fromisoformat(old["time"]) < timedelta(hours=1):
        return old["rate"], ""
    try:
        rate = fetch_rate(client, base)
    except httpx.HTTPError:   # 沒回應、連不上、狀態碼不對，都算掛掉
        if old:
            return old["rate"], ""
        raise
    cache[base] = {"rate": rate, "time": now.isoformat(timespec="minutes")}
    cache_file.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return rate, ""


if __name__ == "__main__":
    with httpx.Client() as client:
        rate, note = cached_rate(client, "USD", datetime.now(), Path(__file__).parent / "rates.json")
    print("1 美元 =", rate, "台幣", note)
