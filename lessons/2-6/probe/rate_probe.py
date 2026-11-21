# check 用（學員不用看）：把 httpx 真的連線換成假回應（不打真網路），跑學員的 rate.py 兩次：200、404
import runpy

import httpx

seen = []


def run(kind):
    def fake(self, request):
        seen.append(request.extensions.get("timeout", {}).get("connect"))
        if kind == "ok":
            return httpx.Response(200, json=[{"date": "2026-11-20", "base": "USD", "quote": "TWD", "rate": 31.234}])
        return httpx.Response(404, json={"status": 404, "message": "not found"})
    httpx.HTTPTransport.handle_request = fake
    try:
        runpy.run_path("rate.py", run_name="__main__")
        print(f"{kind} → 跑完")
    except Exception as exc:
        print(f"{kind} → {type(exc).__name__}")


run("ok")
run("404")
print("timeout 夠長" if seen and min(t or 0 for t in seen) >= 1 else f"timeout 太短：{seen[:1]}")
