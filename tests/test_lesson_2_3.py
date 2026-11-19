"""2-3〈測試先行：pytest〉：作業與 check 的回歸測試（每課自己一個測試檔，不改 test_regressions.py）。

grader 加的（只對寫了它的題目生效）：
  pytest_chaff  學員用 pytest 寫的測試：每個版本（正確版、壞版本）各一個暫存資料夾，用帳本 .venv 的 Python 跑 python -m pytest，讀 junitxml；
                正確版全部通過、每個壞版本至少一個測試變紅。min_tests、wheat、must_use 照 spec。
  uv_deps 的 dev  [dependency-groups] 的 dev 裡有 pytest（uv add --dev pytest）；寫在 dependencies 也算過，多一句提醒。
pytest 用 uv add --dev --offline 從 uv 的快取裝（不連網；沒有快取時這幾條測試會失敗，先在任何地方 uv add --dev pytest 一次）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv 和 git。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, git, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l203"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "2-3"
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


def answer_file(name: str) -> str:
    return (D / "answers" / name).read_text(encoding="utf-8")


def ev(ids: list[str], ledger: Path | None = L) -> grader.Outcome:
    les = grader.load_lesson(LID, COURSE)
    return grader.evaluate(les, ledger, only=[c for c in les.checks if c["id"] in ids])


def by(out: grader.Outcome) -> dict[str, grader.Result]:
    return {r.id: r for r in out.results}


def uv(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([UV, *args], cwd=L, env=grader.child_env(), capture_output=True, text=True)


def add_pytest(dev: bool = True) -> None:
    r = uv("add", *(["--dev"] if dev else []), "pytest", "--offline", "--quiet")
    if r.returncode != 0:
        raise AssertionError("uv add pytest --offline 失敗（uv 的快取裡沒有 pytest？）：" + r.stderr[-400:])


def remove_pytest() -> None:
    text = (L / "pyproject.toml").read_text(encoding="utf-8")
    if "pytest" in text:
        uv("remove", "--dev", "pytest", "--offline", "--quiet")
        uv("remove", "pytest", "--offline", "--quiet")


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


def save(msg: str) -> None:
    git(L, "add", "-A")
    git(L, "commit", "-q", "--allow-empty", "-m", msg)


def fresh_repo() -> None:
    if (L / ".git").exists():
        shutil.rmtree(L / ".git")
    git(L, "init", "-q")


def setUpModule():
    if UV is None or shutil.which("git") is None:
        raise unittest.SkipTest("需要 uv 和 git")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)
    add_pytest()


class Basics(unittest.TestCase):
    def test_lesson_id_forms(self):
        course = grader.course_info(COURSE)
        for raw in ("2-3", "2-03", "２－３"):
            self.assertEqual(grader.normalize_id(raw, course), "2-3")
        self.assertIn("2-3", grader.available_lessons(COURSE))

    def test_start_split_has_no_leftover(self):
        """起點的 split.py 還沒放零頭：100 元三個人分是 [33, 33, 33]；checks_split.py 停在第 5 行（第二條 assert）。"""
        start()
        p = subprocess.run([UV, "run", "--offline", "--quiet", "lessons/2-3/checks_split.py"], cwd=L, env=grader.child_env(),
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("AssertionError", p.stderr)
        self.assertIn('line 5', p.stderr)

    def test_review_letters(self):
        key = json.loads((D / "answers" / "review.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"] for q in key["questions"]], [["A"], ["B"]])

    def test_monthly_examples_add_up(self):
        """docstring 的例子、參考答案的手算值，在正確版上都對。"""
        ns: dict = {}
        exec(compile((D / "reference" / "monthly.py").read_text(encoding="utf-8"), "monthly.py", "exec"), ns)
        f = ns["monthly_total"]
        self.assertEqual(f([("10/31", "晚餐", "餐飲", 150), ("11/03", "午餐", "餐飲", 120)], 11), 120)
        self.assertEqual(f([], 11), 0)


class PytestDep(unittest.TestCase):
    def tearDown(self):
        remove_pytest()
        add_pytest()

    def test_dev_ok(self):
        r = by(ev(["pytest"]))["pytest"]
        self.assertTrue(r.ok, r.detail)
        self.assertNotIn("--dev", r.note)
        text = (L / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("[dependency-groups]", text)

    def test_missing(self):
        remove_pytest()
        r = by(ev(["pytest"]))["pytest"]
        self.assertFalse(r.ok)
        self.assertIn("uv add --dev pytest", r.detail)

    def test_plain_dependencies_ok_with_note(self):
        remove_pytest()
        add_pytest(dev=False)
        r = by(ev(["pytest"]))["pytest"]
        self.assertTrue(r.ok, r.detail)
        self.assertIn("uv add --dev", r.note)


class SplitTests(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_file(self):
        """起點的 test_split.py 只有一個測試：少於 6 個；正確版過；三個壞版本都溜過去（還沒寫滿，先不講是哪一種）。"""
        out = ev(["tsplit"])
        rs = by(out)
        self.assertFalse(rs["tsplit-count"].ok)
        self.assertIn("找到 1 個測試", rs["tsplit-count"].detail)
        self.assertTrue(rs["tsplit-wheat"].ok, rs["tsplit-wheat"].detail)
        for i in (1, 2, 3):
            self.assertFalse(rs[f"tsplit-m{i}"].ok)
            self.assertIn("先寫滿 6 個測試", rs[f"tsplit-m{i}"].detail)
        self.assertTrue(any("抓到 0 個壞版本" in s for s in out.summaries), out.summaries)

    def test_answer_catches_all(self):
        write(mine("tests/test_split.py"), answer_file("test_split.py"))
        out = ev(["tsplit", "tzero"])
        rs = by(out)
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))
        self.assertIn("被 test_split[", rs["tsplit-m1"].note)
        self.assertEqual(rs["tzero-m1"].note, "被 test_no_people 抓到")
        self.assertNotIn("tzero-wheat", rs)
        self.assertNotIn("tzero-count", rs)

    def test_six_easy_cases_miss_m3(self):
        """六組都只有 1 元零頭（或沒有零頭）：零頭全給第一個人的 m3 溜過去，提示講 101 元三個人分。"""
        text = answer_file("test_split.py").replace("(101, 3, [34, 34, 33]),", "(301, 3, [101, 100, 100]),").replace(
            "(10, 4, [3, 3, 2, 2]),", "(9, 4, [3, 2, 2, 2]),")
        write(mine("tests/test_split.py"), text)
        out = ev(["tsplit"])
        rs = by(out)
        self.assertTrue(rs["tsplit-m1"].ok and rs["tsplit-m2"].ok)
        self.assertFalse(rs["tsplit-m3"].ok)
        self.assertIn("101 元三個人分", rs["tsplit-m3"].detail)
        self.assertTrue(any("抓到 2 個壞版本，還有 1 個溜過去：" in s for s in out.summaries), out.summaries)

    def test_wrong_expectation(self):
        text = answer_file("test_split.py").replace("(100, 3, [34, 33, 33]),", "(100, 3, [33, 33, 34]),")
        write(mine("tests/test_split.py"), text)
        r = by(ev(["tsplit"]))["tsplit-wheat"]
        self.assertFalse(r.ok)
        self.assertIn("test_split[100-3-expected1] 在正確版上就沒過", r.detail)

    def test_syntax_error(self):
        write(mine("tests/test_split.py"), "from split import split\n\ndef test_a()\n    assert split(3, 3) == [1, 1, 1]\n")
        r = by(ev(["tsplit"]))["tsplit-wheat"]
        self.assertFalse(r.ok)
        self.assertIn("第 3 行有語法錯誤", r.detail)

    def test_import_typo(self):
        write(mine("tests/test_split.py"), "from splt import split\n\n\ndef test_a():\n    assert split(3, 3) == [1, 1, 1]\n")
        r = by(ev(["tsplit"]))["tsplit-wheat"]
        self.assertFalse(r.ok)
        self.assertIn("收集測試的時候就出錯了", r.detail)
        self.assertIn("splt", r.detail)

    def test_no_test_prefix(self):
        write(mine("tests/test_split.py"), "from split import split\n\n\ndef check_a():\n    assert split(3, 3) == [1, 1, 1]\n")
        rs = by(ev(["tsplit"]))
        self.assertFalse(rs["tsplit-wheat"].ok)
        self.assertIn("test_ 開頭", rs["tsplit-wheat"].detail)

    def test_ledger_untouched(self):
        write(mine("tests/test_split.py"), answer_file("test_split.py"))
        before = snapshot(L)
        ev(["tsplit", "tzero", "tdates"])
        self.assertEqual(snapshot(L), before)

    def test_without_pytest(self):
        remove_pytest()
        uv("sync", "--offline", "--quiet")
        try:
            write(mine("tests/test_split.py"), answer_file("test_split.py"))
            r = by(ev(["tsplit"]))["tsplit-wheat"]
            self.assertFalse(r.ok)
            self.assertIn("還沒裝 pytest", r.detail)
            self.assertIn("uv add --dev pytest", r.detail)
        finally:
            add_pytest()


class SplitCode(unittest.TestCase):
    def test_start_fails_leftover(self):
        start()
        rs = by(ev(["split-1", "split-2", "split-0"]))
        self.assertFalse(rs["split-1"].ok)
        self.assertFalse(rs["split-0"].ok)

    def test_fixed_passes(self):
        start()
        write(mine("split.py"), (D / "reference" / "split.py").read_text(encoding="utf-8"))
        rs = by(ev(["split-1", "split-2", "split-0"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_two_line_fix_without_raise(self):
        """只加了零頭那兩行（影片第①圈的樣子）：零頭的兩題過，人數 0 那題還沒過（第②圈才加）。"""
        start()
        text = mine("split.py").read_text(encoding="utf-8").replace(
            "    return shares", "    for i in range(total % people):\n        shares[i] = shares[i] + 1\n    return shares")
        write(mine("split.py"), text)
        rs = by(ev(["split-1", "split-2", "split-0"]))
        self.assertTrue(rs["split-1"].ok and rs["split-2"].ok)
        self.assertFalse(rs["split-0"].ok)


class DatesTests(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_needs_monkeypatch(self):
        rs = by(ev(["tdates"]))
        self.assertFalse(rs["tdates-wheat"].ok)
        self.assertIn("還沒有用 monkeypatch", rs["tdates-wheat"].detail)

    def test_answer_catches_all(self):
        write(mine("tests/test_dates.py"), answer_file("test_dates.py"))
        rs = by(ev(["tdates"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_two_digit_day_misses_padding(self):
        """挑 11/13：月和日都是兩位數，沒補零的 m3 溜過去。"""
        write(mine("tests/test_dates.py"), answer_file("test_dates.py").replace("date(2026, 11, 3)", "date(2026, 11, 13)").replace('"11/03"', '"11/13"'))
        rs = by(ev(["tdates"]))
        self.assertTrue(rs["tdates-m1"].ok and rs["tdates-m2"].ok)
        self.assertFalse(rs["tdates-m3"].ok)
        self.assertIn("沒有補零", rs["tdates-m3"].detail)


class MonthlyTests(unittest.TestCase):
    def setUp(self):
        start()

    def test_missing_file_hint(self):
        r = by(ev(["tmonthly"]))["tmonthly-wheat"]
        self.assertFalse(r.ok)
        self.assertIn("cp lessons/2-3/ai_test_monthly.py", r.detail)

    def test_frozen_ai_tests_catch_only_m4(self):
        """總企劃：用 4 個壞版本跑 AI 寫的測試，只抓到 1 個（課程凍結的版本只抓得到「空的交回 None」）。"""
        shutil.copyfile(mine("ai_test_monthly.py"), mine("tests/test_monthly.py"))
        out = ev(["tmonthly"])
        rs = by(out)
        self.assertTrue(rs["tmonthly-count"].ok)
        self.assertTrue(rs["tmonthly-wheat"].ok, rs["tmonthly-wheat"].detail)
        self.assertEqual([rs[f"tmonthly-m{i}"].ok for i in (1, 2, 3, 4)], [False, False, False, True])
        self.assertEqual(rs["tmonthly-m4"].note, "被 test_empty 抓到")
        self.assertIn("test_monthly.py 抓到 1 個壞版本，還有 3 個溜過去：", out.summaries)
        for s in out.summaries:
            self.assertLessEqual(grader._cols(s), 68, s)

    def test_answer_catches_all(self):
        write(mine("tests/test_monthly.py"), answer_file("test_monthly.py"))
        out = ev(["tmonthly"])
        for k, r in by(out).items():
            self.assertTrue(r.ok, (k, r.detail))
        self.assertIn("test_monthly.py 把 4 個壞版本全部抓到了。", out.summaries)


class Forms(unittest.TestCase):
    def setUp(self):
        start()

    def test_review(self):
        answer("review.txt", ["A", "B"])
        out = ev(["review"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_edges_needs_three(self):
        fill("edges.md", {"邊界情況：": "人數是 0", "我的決定和理由：": "加，需求卡說至少 1 個人"})
        self.assertTrue(by(ev(["edges"]))["edges"].ok)
        write(mine("edges.md"), "邊界情況：人數是 0\n我的決定和理由：加，需求卡寫了\n")
        r = by(ev(["edges"]))["edges"]
        self.assertFalse(r.ok)
        self.assertIn("第 2 條", r.detail)

    def test_saved_hint_when_not_saved(self):
        """還沒按交辦前的存檔點：提示照 2-3 的寫法（請 AI 寫測試，不是改 monthly.py）。"""
        fresh_repo()
        write(L / "README.md", "# 帳本\n")
        git(L, "add", "README.md")
        git(L, "commit", "-q", "-m", "第一個存檔點")
        git(L, "commit", "-q", "--allow-empty", "-m", "帳本 v0")
        r = by(ev(["saved"]))["saved"]
        self.assertFalse(r.ok)
        self.assertIn("交給 AI 寫測試之前", r.detail)
        self.assertNotIn("Discard", r.detail)

    def test_saved_before_and_committed(self):
        fresh_repo()
        save("交辦前")
        write(mine("tests/test_monthly.py"), answer_file("test_monthly.py"))
        save("月合計測試")
        r = by(ev(["saved"]))["saved"]
        self.assertTrue(r.ok, r.detail)


if __name__ == "__main__":
    unittest.main()
