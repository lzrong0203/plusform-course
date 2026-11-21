# 範例示意：把 rate_cache.py 交給 AI 寫，它交回來的樣子
#   （課程凍結的版本，第③圈拿來驗收）
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
    except httpx.HTTPStatusError:   # API 掛掉：用上一次的值
        if old:
            return old["rate"], f"查不到新的匯率，用上一次的（{old['time']}）"
        raise
    cache[base] = {"rate": rate, "time": now.isoformat(timespec="minutes")}
    cache_file.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return rate, ""


if __name__ == "__main__":
    with httpx.Client() as client:
        rate, note = cached_rate(client, "USD", datetime.now(), Path(__file__).parent / "rates.json")
    print("1 美元 =", rate, "台幣", note)
