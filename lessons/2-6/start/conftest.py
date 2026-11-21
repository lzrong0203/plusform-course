# 課程準備：測試的時候不准打真網路。
#   httpx 真的要連出去時，會被這裡擋下來、直接報錯；MockTransport 的假回應不受影響。
#   （放在 lessons/2-6，pytest 才找得到同一個資料夾的 rates.py、rate_cache.py）
import httpx
import pytest


@pytest.fixture(autouse=True)
def no_real_network(monkeypatch):
    def blocked(self, request):
        raise RuntimeError(f"測試打了真網路：{request.url}")
    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", blocked)
