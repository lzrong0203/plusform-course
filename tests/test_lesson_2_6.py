"""2-6〈呼叫網路 API：狀態碼、逾時、假回應〉：作業與 check 的回歸測試（每課自己一個測試檔，不改 test_regressions.py）。

沒有新加 grader 欄位：用前幾課就有的 uv_deps、run 的 sandbox（copy、probe、steps；probe 把 httpx 真的連線換成假回應）、
answers、filled、pytest_chaff（extra_files 放 conftest.py＝擋真網路、rates.py）、git_commits（saved_before）。
**全部不打真網路**：rate.py、jpy.py 只在 check 的 probe 裡跑（假回應）；這個測試檔也不直接執行它們。
httpx、pytest 用 uv add --offline 從 uv 的快取裝（不連網；沒有快取時這幾條測試會失敗，先在任何地方 uv add httpx、uv add --dev pytest 一次）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv 和 git。
"""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, git, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l206"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "2-6"
D = COURSE / "lessons" / LID


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def mine(name: str) -> Path:
    return L / "lessons" / LID / name


def start() -> Path:
    dest = L / "lessons" / LID
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(D / "start", dest)
    return dest


def ref(name: str) -> None:
    shutil.copyfile(D / "reference" / name, mine(name))


def ev(ids: list[str], ledger: Path | None = L) -> grader.Outcome:
    les = grader.load_lesson(LID, COURSE)
    return grader.evaluate(les, ledger, only=[c for c in les.checks if c["id"] in ids])


def by(out: grader.Outcome) -> dict[str, grader.Result]:
    return {r.id: r for r in out.results}


def uv(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([UV, *args], cwd=L, env=grader.child_env(), capture_output=True, text=True)


def run_py(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([UV, "run", "--offline", "--quiet", *args], cwd=L, env=grader.child_env(), capture_output=True, text=True)


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def fill(name: str, values: dict[str, str]) -> None:
    p = mine(name)
    out = []
    for ln in p.read_text(encoding="utf-8").splitlines():
        hit = next((k for k in values if ln.startswith(k)), None)
        out.append(ln + values[hit] if hit else ln)
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def setUpModule():
    if UV is None or shutil.which("git") is None:
        raise unittest.SkipTest("需要 uv 和 git")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)
    r = uv("add", "--dev", "pytest", "--offline", "--quiet")
    if r.returncode != 0:
        raise AssertionError("uv add pytest --offline 失敗（uv 的快取裡沒有 pytest？）：" + r.stderr[-400:])


class Basics(unittest.TestCase):
    def test_lesson_id_forms(self):
        course = grader.course_info(COURSE)
        for raw in ("2-6", "2-06", "２－６"):
            self.assertEqual(grader.normalize_id(raw, course), "2-6")
        self.assertIn("2-6", grader.available_lessons(COURSE))

    def test_no_real_network_in_lesson_tests(self):
        """起點的測試只用 MockTransport；課程的 conftest.py 擋住真的連線（handle_request 換掉）。"""
        for name in ("start/tests/test_rates.py", "start/tests/test_cache.py", "answers/test_rates.py", "answers/test_cache.py"):
            text = (D / name).read_text(encoding="utf-8")
            self.assertIn("MockTransport", text, name)
            self.assertNotIn("httpx.get(", text, name)
        self.assertIn("HTTPTransport, \"handle_request\"", (D / "start" / "conftest.py").read_text(encoding="utf-8"))

    def test_probes_patch_network(self):
        """check 用的 probe 一律先換掉真的連線（不打真網路）。"""
        for name in ("rate_probe.py", "jpy_probe.py"):
            self.assertIn("httpx.HTTPTransport.handle_request = fake", (D / "probe" / name).read_text(encoding="utf-8"), name)
        self.assertIn("MockTransport", (D / "probe" / "cache_probe.py").read_text(encoding="utf-8"))


class Ring1(unittest.TestCase):
    def setUp(self):
        start()

    def test_httpx_missing_then_added(self):
        if "httpx" in (L / "pyproject.toml").read_text(encoding="utf-8"):   # 別的測試先裝過了
            p = uv("remove", "httpx", "--offline", "--quiet")
            self.assertEqual(p.returncode, 0, p.stderr[-400:])
        r = by(ev(["httpx"]))["httpx"]
        self.assertFalse(r.ok)
        p = uv("add", "httpx", "--offline", "--quiet")
        self.assertEqual(p.returncode, 0, p.stderr[-400:])
        r = by(ev(["httpx"]))["httpx"]
        self.assertTrue(r.ok, r.detail)

    def _need_httpx(self):
        if "httpx" not in (L / "pyproject.toml").read_text(encoding="utf-8"):
            p = uv("add", "httpx", "--offline", "--quiet")
            self.assertEqual(p.returncode, 0, p.stderr[-400:])

    def test_start_rate_fails_reference_passes(self):
        self._need_httpx()
        r = by(ev(["rate"]))["rate"]
        self.assertFalse(r.ok)
        ref("rate.py")
        r = by(ev(["rate"]))["rate"]
        self.assertTrue(r.ok, r.detail)

    def test_rate_without_raise_is_keyerror(self):
        """影片第①圈：只打了最後一行、沒有 raise_for_status：404 變成 KeyError（check 不過、提示講 raise_for_status）。"""
        self._need_httpx()
        text = (D / "start" / "rate.py").read_text(encoding="utf-8").replace("# 換你寫：印出「1 美元 = ○○ 台幣」", 'print("1 美元 =", data[0]["rate"], "台幣")')
        write(mine("rate.py"), text)
        r = by(ev(["rate"]))["rate"]
        self.assertFalse(r.ok)
        self.assertIn("404 → KeyError", r.detail)
        self.assertIn("raise_for_status", r.detail)

    def test_rate_tiny_timeout_left(self):
        """第①圈試過的 timeout=0.001 忘了改回來：check 不過。"""
        self._need_httpx()
        write(mine("rate.py"), (D / "reference" / "rate.py").read_text(encoding="utf-8").replace("timeout=5", "timeout=0.001"))
        r = by(ev(["rate"]))["rate"]
        self.assertFalse(r.ok)
        self.assertIn("timeout 太短", r.detail)

    def test_fake_tests(self):
        """起點只有 test_ok：兩個壞版本都溜過去；補上 test_429 就都抓到。"""
        self._need_httpx()
        rs = by(ev(["fake"]))
        self.assertFalse(rs["fake-m1"].ok)
        write(mine("tests/test_rates.py"), (D / "answers" / "test_rates.py").read_text(encoding="utf-8"))
        rs = by(ev(["fake"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_real_network_test_is_blocked(self):
        """學員的測試要是自己開 httpx.Client() 打真網路：conftest 擋下來，正確版就沒過。"""
        self._need_httpx()
        text = (D / "answers" / "test_rates.py").read_text(encoding="utf-8") + '\n\ndef test_real():\n    assert fetch_rate(httpx.Client(), "USD") > 0\n'
        write(mine("tests/test_rates.py"), text)
        rs = by(ev(["fake"]))
        self.assertFalse(rs["fake-wheat"].ok)

    def test_lesson_pytest_offline(self):
        """在帳本裡跑 uv run pytest lessons/2-6/tests/test_rates.py（影片第①圈的指令）：2 passed，不連網。"""
        self._need_httpx()
        write(mine("tests/test_rates.py"), (D / "answers" / "test_rates.py").read_text(encoding="utf-8"))
        p = run_py("pytest", "-q", "-p", "no:cacheprovider", "lessons/2-6/tests/test_rates.py")
        self.assertEqual(p.returncode, 0, p.stdout[-800:] + p.stderr[-400:])
        self.assertIn("2 passed", p.stdout)

    def test_api_answers(self):
        answer("api.txt", ["B", "A", "C"])
        rs = by(ev(["api"]))
        self.assertTrue(all(r.ok for r in rs.values()), [(r.id, r.detail) for r in rs.values()])

    def test_ledger_untouched(self):
        self._need_httpx()
        ref("rate.py")
        before = snapshot(L)
        ev(["rate", "fake"])
        self.assertEqual(snapshot(L), before)


class Ring2(unittest.TestCase):
    def setUp(self):
        start()
        if "httpx" not in (L / "pyproject.toml").read_text(encoding="utf-8"):
            uv("add", "httpx", "--offline", "--quiet")

    def test_start_jpy_422(self):
        r = by(ev(["jpy"]))["jpy"]
        self.assertFalse(r.ok)
        self.assertIn("422", r.detail)
        self.assertIn("quotes", r.detail)

    def test_reference_and_forms(self):
        ref("jpy.py")
        answer("codes.txt", ["A", "C", "B"])
        fill("docs.md", {"我想查的：": "日圓換台幣", "拿到的狀態碼和錯誤訊息：": "422 unknown parameter", "我查的官方文件（網址）：": "frankfurter.dev",
                         "文件寫的參數名字：": "quotes", "家教怎麼帶我查的：": "問我文件寫什麼"})
        rs = by(ev(["jpy", "codes", "docs"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))


class Ring3(unittest.TestCase):
    def setUp(self):
        start()
        if "httpx" not in (L / "pyproject.toml").read_text(encoding="utf-8"):
            uv("add", "httpx", "--offline", "--quiet")

    def test_start_test_catches_two(self):
        """起點的 test_cache.py（test_api_down 還沒有 assert）：正確版過、m1 m4 抓到、m2 m3 溜過去。"""
        rs = by(ev(["accept"]))
        self.assertTrue(rs["accept-wheat"].ok, rs["accept-wheat"].detail)
        self.assertTrue(rs["accept-m1"].ok)
        self.assertTrue(rs["accept-m4"].ok)
        self.assertFalse(rs["accept-m2"].ok)
        self.assertFalse(rs["accept-m3"].ok)

    def test_asserts_catch_all(self):
        """影片裡熊補的兩行 assert：四個壞版本都抓到。"""
        write(mine("tests/test_cache.py"), (D / "answers" / "test_cache.py").read_text(encoding="utf-8"))
        rs = by(ev(["accept"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_ai_version_pytest_in_ledger(self):
        """影片第③圈：課程凍結的 AI 版本放進 rate_cache.py，uv run pytest lessons/2-6 → test_api_down 紅（ConnectTimeout）；改成 HTTPError → 全過。"""
        write(mine("tests/test_cache.py"), (D / "answers" / "test_cache.py").read_text(encoding="utf-8"))
        write(mine("tests/test_rates.py"), (D / "answers" / "test_rates.py").read_text(encoding="utf-8"))
        shutil.copyfile(mine("ai_rate_cache.py"), mine("rate_cache.py"))
        p = run_py("pytest", "-q", "-p", "no:cacheprovider", "lessons/2-6")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("1 failed, 3 passed", p.stdout)
        self.assertIn("ConnectTimeout", p.stdout)
        write(mine("rate_cache.py"), mine("ai_rate_cache.py").read_text(encoding="utf-8").replace("except httpx.HTTPStatusError:", "except httpx.HTTPError:"))
        p = run_py("pytest", "-q", "-p", "no:cacheprovider", "lessons/2-6")
        self.assertEqual(p.returncode, 0, p.stdout[-800:])
        self.assertIn("4 passed", p.stdout)

    def test_hidden(self):
        """隱藏情況：沒有 rate_cache.py 時提示 cp；AI 版本（只接 HTTPStatusError）連不上就當掉；改成 HTTPError 就過。"""
        r = by(ev(["hidden"]))["hidden"]
        self.assertFalse(r.ok)
        self.assertIn("cp lessons/2-6/ai_rate_cache.py", r.detail)
        shutil.copyfile(mine("ai_rate_cache.py"), mine("rate_cache.py"))
        r = by(ev(["hidden"]))["hidden"]
        self.assertFalse(r.ok)
        self.assertIn("連不上 當掉", r.detail)
        write(mine("rate_cache.py"), mine("ai_rate_cache.py").read_text(encoding="utf-8").replace("except httpx.HTTPStatusError:", "except httpx.HTTPError:"))
        r = by(ev(["hidden"]))["hidden"]
        self.assertTrue(r.ok, r.detail)

    def test_saved_and_decision(self):
        if (L / ".git").exists():
            shutil.rmtree(L / ".git")
        git(L, "init", "-q")
        git(L, "add", "-A")
        git(L, "commit", "-q", "-m", "交辦前")
        ref("rate_cache.py")
        write(mine("tests/test_cache.py"), (D / "answers" / "test_cache.py").read_text(encoding="utf-8"))
        git(L, "add", "-A")
        git(L, "commit", "-q", "-m", "匯率快取")
        fill("decision.md", {"它跑了什麼指令：": "uv run pytest lessons/2-6", "uv run pytest 的結果：": "1 failed", "哪個測試沒過、為什麼：": "test_api_down，只接 HTTPStatusError",
                             "我改了哪一行：": "except 那一行", "收不收，為什麼：": "改好才收"})
        rs = by(ev(["saved", "decision"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))


if __name__ == "__main__":
    unittest.main()
