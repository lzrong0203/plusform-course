# check 用（學員不用看）：假的匯率服務（跟 Frankfurter 一樣：參數名字不認得就回 422），跑學員的 jpy.py，不打真網路
import runpy

import httpx

KNOWN = {"base", "quotes", "providers", "date", "from", "to"}


def fake(self, request):
    params = dict(request.url.params)
    bad = [k for k in params if k not in KNOWN]
    if bad:
        return httpx.Response(422, json={"status": 422, "message": f"unknown parameter: {bad[0]}"})
    if params.get("base", "").upper() == "JPY" and "TWD" in params.get("quotes", "").upper():
        return httpx.Response(200, json=[{"date": "2026-11-20", "base": "JPY", "quote": "TWD", "rate": 0.2071}])
    return httpx.Response(200, json=[{"date": "2026-11-20", "base": params.get("base", "EUR"), "quote": "USD", "rate": 9.99}])


httpx.HTTPTransport.handle_request = fake
try:
    runpy.run_path("jpy.py", run_name="__main__")
except httpx.HTTPStatusError as exc:
    print(f"拿到 {exc.response.status_code}：{exc.response.json().get('message')}")
except Exception as exc:
    print(f"當掉：{type(exc).__name__}")
