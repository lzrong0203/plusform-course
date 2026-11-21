# 2-6 第①圈：用假回應測 fetch_rate（不打真網路）
import httpx
import pytest

from rates import fetch_rate


def fake_client(handler):
    """做一個假的 client：要連網路的時候，改成問 handler 要回應。"""
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_ok():
    def handler(request):
        return httpx.Response(200, json=[{"date": "2026-11-20", "base": "USD", "quote": "TWD", "rate": 32.5}])
    assert fetch_rate(fake_client(handler), "USD") == 32.5


def test_429():
    def handler(request):
        return httpx.Response(429)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_rate(fake_client(handler), "USD")
