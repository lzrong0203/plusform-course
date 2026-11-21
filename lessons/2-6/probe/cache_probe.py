# check 用（學員不用看）：另一組沒看過的情況（不同的匯率、503、429、連不上），呼叫學員的 cached_rate；全部是假回應，不打真網路
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import httpx

from rate_cache import cached_rate

calls = []


def client(kind, rate=31.0):
    def handler(request):
        calls.append(kind)
        if kind == "ok":
            return httpx.Response(200, json=[{"date": "2026-12-01", "base": "JPY", "quote": "TWD", "rate": rate}])
        if kind == "503":
            return httpx.Response(503, json={"status": 503, "message": "unavailable"})
        if kind == "429":
            return httpx.Response(429, headers={"Retry-After": "60"}, json={"status": 429, "message": "too many requests"})
        raise httpx.ConnectError("連不上")
    return httpx.Client(transport=httpx.MockTransport(handler))


def show(label, got):
    rate, note = got
    print(label, rate, "有提示" if note and "上一次" in note else f"沒有提示：{note!r}")


cache = Path(tempfile.mkdtemp(prefix="plusform-cache-")) / "cache.json"
t0 = datetime(2026, 12, 1, 9, 0)
print("第一次", cached_rate(client("ok", 0.21), "JPY", t0, cache)[0])
print("半小時後", cached_rate(client("ok", 0.99), "JPY", t0 + timedelta(minutes=30), cache)[0], f"（問了 {len(calls)} 次）")
print("一小時又一分後", cached_rate(client("ok", 0.22), "JPY", t0 + timedelta(minutes=61), cache)[0], f"（問了 {len(calls)} 次）")
for i, kind in enumerate(["503", "429", "連不上"]):
    try:
        show(kind, cached_rate(client(kind), "JPY", t0 + timedelta(hours=3 + i), cache))
    except Exception as exc:
        print(kind, "當掉：", type(exc).__name__)
