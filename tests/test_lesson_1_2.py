"""1-2〈變數：給資料取名字〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

重點：第①圈追蹤表題（右邊先算、改了一個名字不會回頭改別的、沒有等號就沒放進去）、自己寫的合計；
第②圈 4 則 AI 意見；第③圈 expected_text 抓三個「名字」的壞版本，其中合計取名 sum 的那一版印完合計就當掉。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l12"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-2"
D = COURSE / "lessons" / LID
TEACHER = (D / "answers" / "expected.txt").read_text(encoding="utf-8")
TRACE = ["250", "250", "60", "130", "130", "180"]
AI = ["不採用", "不採用", "採用", "不採用"]


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def start() -> Path:
    dest = L / "lessons" / LID
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(D / "start", dest)
    return dest


def fill(name: str, answers: list[str]) -> None:
    p = L / "lessons" / LID / name
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def ev(ids: list[str], ledger: Path | None = L) -> grader.Outcome:
    les = grader.load_lesson(LID, COURSE)
    return grader.evaluate(les, ledger, only=[c for c in les.checks if c["id"] in ids])


def part(out: grader.Outcome, suffix: str) -> grader.Result:
    return next(r for r in out.results if r.id.rsplit("-", 1)[-1] == suffix)


def expected(text: str) -> grader.Outcome:
    write(L / "lessons" / LID / "expected.txt", text)
    return ev(["r3"])


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class ExpectedText(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_answer_catches_all_three_name_bugs(self):
        out = expected(TEACHER)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        m1 = part(out, "m1").note
        self.assertIn("被第 5 行抓到", m1)              # 合計取名 sum：印完合計，第 5 行（飲食）就當掉
        self.assertIn("跑到一半當掉", m1)
        self.assertEqual(part(out, "m2").note, "被第 3 行抓到")   # 捷運印成晚餐的錢
        self.assertEqual(part(out, "m3").note, "被第 6 行抓到")   # total 放了兩次，錢包扣錯
        self.assertIn("你的預期輸出把 3 個壞版本全部抓到了。", out.summaries)

    def test_start_file_is_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("「？」沒填完", part(out, "count").detail)
        self.assertFalse(any(r.ok for r in out.results))

    def test_only_the_first_four_lines_cannot_tell_the_sum_version_apart(self):
        """只寫到合計的人：行數不夠、正確版也不成立；而且前四行在 sum 那一版上都一樣（當掉以前印的都對）。"""
        lines = TEACHER.splitlines()
        write(L / "lessons" / LID / "expected.txt", "\n".join(lines[:4]) + "\n")
        les = grader.load_lesson(LID, COURSE)
        ctx, chk = grader.build(les, L, only=[c for c in les.checks if c["id"] == "r3"])
        parsed = chk[0].parse()
        st, _ = chk[0].statuses(parsed.checks, parsed.marks)
        self.assertTrue(all(row["status"] == "pass" for row in st["m1"][:4]))
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("正確版一共印出 6 行，你寫了 4 行", part(out, "wheat").detail)

    def test_no_spaces_around_the_number_is_a_different_line(self):
        out = expected(TEACHER.replace("合計 205 元", "合計205元"))
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("第 4 行", part(out, "wheat").detail)
        self.assertIn("空格", part(out, "wheat").detail)

    def test_forgetting_to_subtract_is_wrong_on_the_reference(self):
        out = expected(TEACHER.replace("錢包剩下 95 元", "錢包剩下 300 元"))
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("第 6 行", part(out, "wheat").detail)
        self.assertFalse(part(out, "m3").ok)   # 錢包那一行寫錯了，就抓不到扣錯錢的那一版

    def test_comments_crlf_and_fullwidth_spaces_free_layout(self):
        text = "# 我的預期輸出\n\n" + TEACHER + "\n# 寫完了\n"
        out = expected(text.replace("\n", "\r\n"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class FirstRing(unittest.TestCase):
    def setUp(self):
        start()

    def test_trace_answers(self):
        fill("trace.txt", ["250", "250 元", "60", "130", "130", "180"])
        out = ev(["trace"])
        self.assertEqual([r.ok for r in out.results], [True] * 6, [r.detail for r in out.results])

    def test_trace_common_mistakes_get_the_right_hint(self):
        # 以為改了 juice，money 會跟著變；以為沒有等號那一行也加進去了
        fill("trace.txt", ["250", "240", "60", "130", "155", "205"])
        out = ev(["trace"])
        self.assertEqual([r.ok for r in out.results], [True, False, True, True, False, False])
        self.assertIn("money 會不會跟著變", out.results[1].detail)
        self.assertIn("「total =」", out.results[4].detail)

    def test_total_reference_passes_and_start_does_not(self):
        self.assertFalse(ev(["total"]).results[0].ok)
        shutil.copy(D / "reference" / "total.py", L / "lessons" / LID / "total.py")
        r = ev(["total"]).results[0]
        self.assertTrue(r.ok, r.detail)

    def test_total_with_wrong_case_shows_the_name_error(self):
        src = (D / "reference" / "total.py").read_text(encoding="utf-8").replace('print("今天花了", total, "元")', 'print("今天花了", Total, "元")')
        write(L / "lessons" / LID / "total.py", src)
        r = ev(["total"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("NameError", r.detail)
        self.assertIn("Total", r.detail)

    def test_total_without_assignment_prints_the_wrong_total(self):
        """只寫 juice + dinner + mrt、沒有 total =：total 不存在 → NameError（跟影片裡果凍兔少寫等號同一類）。"""
        src = (D / "reference" / "total.py").read_text(encoding="utf-8").replace("total = juice + dinner + mrt", "juice + dinner + mrt")
        write(L / "lessons" / LID / "total.py", src)
        r = ev(["total"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("NameError", r.detail)

    def test_wallet_example_runs(self):
        env = grader.Env(L)
        p = env.run_file(L / "lessons" / LID / "wallet.py")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.split(), ["100", "65"])


class SecondRing(unittest.TestCase):
    def setUp(self):
        start()

    def test_ai_answers(self):
        fill("ai_review.txt", ["不採用", "不用", "採用", " 不 採 用 "])
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [True] * 4, [r.detail for r in out.results])

    def test_believing_python_ignores_case_is_wrong(self):
        fill("ai_review.txt", ["不採用", "採用", "採用", "不採用"])
        out = ev(["ai"])
        self.assertFalse(out.results[1].ok)
        self.assertIn("Total", out.results[1].detail)

    def test_record_is_self_assessed_and_not_checked(self):
        les = grader.load_lesson(LID, COURSE)
        files = {c.get("file") or c.get("student_file") for c in les.checks}
        self.assertNotIn("lessons/1-2/record.md", files)
        self.assertTrue((D / "start" / "record.md").is_file())
        self.assertTrue((D / "answers" / "record_example.md").is_file())


class Flow(unittest.TestCase):
    def test_full_run_through_check_py(self):
        """check.py 1-02（課號補 0 也認得）：猜 14、全對 16 題。"""
        start()
        home = fresh_dir("l12_home")
        env = make_env(home, now="2026-11-16T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        work = L / "lessons" / LID
        shutil.rmtree(work)
        r = run_check(["start", "1-02"], env, stdin="")
        self.assertIn("uv run check.py 1-2", r.stdout)
        shutil.copy(D / "reference" / "total.py", work / "total.py")
        write(work / "expected.txt", TEACHER)
        fill("trace.txt", TRACE)
        fill("ai_review.txt", AI)
        r = run_check(["1-02", "--predict", "14", "--no-review"], env)
        self.assertIn("16／16", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的預期輸出把 3 個壞版本全部抓到了。", r.stdout)


if __name__ == "__main__":
    unittest.main()
