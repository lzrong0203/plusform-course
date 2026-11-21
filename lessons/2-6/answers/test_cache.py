# 2-6 第③圈：快取與 API 掛掉的驗收（先寫好，再把 rate_cache.py 交給 AI 寫；全部用假回應）
from datetime import datetime

import httpx

from rate_cache import cached_rate

TEN = datetime(2026, 11, 20, 10, 0)
NOON = datetime(2026, 11, 20, 12, 0)


def ok_client(calls):
    """假的匯率服務：被問一次就在 calls 記一筆，回答 1 美元 = 32.5 台幣。"""
    def handler(request):
        calls.append(request.url)
        return httpx.Response(200, json=[{"date": "2026-11-20", "base": "USD", "quote": "TWD", "rate": 32.5}])
    return httpx.Client(transport=httpx.MockTransport(handler))


def down_client():
    """假的匯率服務：掛掉了，等不到回應。"""
    def handler(request):
        raise httpx.ConnectTimeout("沒回應")
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_cache_one_hour(tmp_path):
    calls = []
    cache = tmp_path / "rates.json"
    assert cached_rate(ok_client(calls), "USD", TEN, cache)[0] == 32.5
    cached_rate(ok_client(calls), "USD", datetime(2026, 11, 20, 10, 30), cache)
    assert len(calls) == 1   # 一小時內：用快取，不再問 API
    cached_rate(ok_client(calls), "USD", datetime(2026, 11, 20, 11, 1), cache)
    assert len(calls) == 2   # 超過一小時：重新問


def test_api_down(tmp_path):
    cache = tmp_path / "rates.json"
    cached_rate(ok_client([]), "USD", TEN, cache)   # 十點查過一次
    rate, note = cached_rate(down_client(), "USD", NOON, cache)   # 十二點 API 掛了
    assert rate == 32.5
    assert "上一次" in note
