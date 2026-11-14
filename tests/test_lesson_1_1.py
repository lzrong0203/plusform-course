"""1-1〈print、註解、程式一行一行跑〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

重點是第③圈的 chaff 新模式 expected_text（學員把整段預期輸出寫進 expected.txt，跟正確版與 3 個壞版本一行一行、連空行一起比）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l11"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-1"
D = COURSE / "lessons" / LID
TEACHER = (D / "answers" / "expected.txt").read_text(encoding="utf-8")


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

    def test_teacher_answer_catches_all_three_versions(self):
        out = expected(TEACHER)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 4 行抓到")   # 多印一行空白：第 4 行應該是第一筆，它印成空行
        self.assertEqual(part(out, "m2").note, "被第 3 行抓到")   # 多一個空格
        self.assertEqual(part(out, "m3").note, "被第 6 行抓到")   # 少印最後一筆
        self.assertIn("你的預期輸出把 3 個壞版本全部抓到了。", out.summaries)

    def test_start_file_is_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("「？」沒填完", part(out, "count").detail)
        self.assertFalse(any(r.ok for r in out.results))

    def test_comments_crlf_trailing_blank_lines_and_halfwidth_colon_are_fine(self):
        text = "# 我的預期輸出\n\n" + TEACHER.replace("：", ":") + "\n\n# 寫完了\n"
        out = expected(text.replace("\n", "\r\n"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_one_extra_space_is_a_different_line(self):
        out = expected(TEACHER.replace("收據：第 1 張", "收據： 第 1 張"))
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("第 3 行", part(out, "wheat").detail)
        self.assertIn("空格", part(out, "wheat").detail)
        self.assertFalse(part(out, "m2").ok)   # 寫得跟壞版本一樣，就抓不到它

    def test_blank_line_in_the_middle_counts(self):
        lines = TEACHER.splitlines()
        out = expected("\n".join(lines[:3] + [""] + lines[3:]) + "\n")
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("空白的一行", part(out, "wheat").detail)
        self.assertFalse(part(out, "m1").ok)   # 寫得跟多印空行的版本一樣

    def test_missing_lines_are_reported_by_the_line_count(self):
        lines = TEACHER.splitlines()
        out = expected("\n".join(lines[:5]) + "\n")   # 少寫最後一行
        self.assertFalse(part(out, "count").ok)   # 這課要至少 6 行
        self.assertIn("正確版一共印出 6 行，你寫了 5 行", part(out, "wheat").detail)

    def test_extra_line_at_the_end_is_caught_by_the_line_count(self):
        out = expected(TEACHER + "謝謝光臨\n")
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("沒有印到這一行", part(out, "wheat").detail)

    def test_version_that_crashes_halfway_is_compared_line_by_line(self):
        """跑到一半當掉的版本：照當掉前印出的比，不整版算 error（1-2 的 sum 壞版本要用；validate 才不會判成「一跑就當掉」）。"""
        root = fresh_dir("l11_crash_course")
        shutil.copytree(COURSE, root / "c", ignore=lambda folder, names: [n for n in names if n in {".git", "__pycache__"} or (Path(folder) == COURSE and n == "tests")])
        m1 = root / "c" / "lessons" / LID / "mutants" / "print_receipt_m1.py"
        src = (root / "c" / "lessons" / LID / "reference" / "print_receipt.py").read_text(encoding="utf-8")
        write(m1, src.replace('print("11/02 公車 15 元")', 'print("11/02 公車 15 元"[99])'))   # 印完五行，第六行當掉
        les = grader.load_lesson(LID, root / "c")
        spec = [c for c in les.checks if c["id"] == "r3"]
        f = write(BASE / "teacher_expected.txt", TEACHER)
        env = grader.Env(None, local=True)
        out = grader.evaluate(les, None, env=env, overrides={"lessons/1-1/expected.txt": f}, only=spec)
        r = part(out, "m1")
        self.assertTrue(r.ok)
        self.assertIn("被第 6 行抓到", r.note)
        self.assertIn("跑到一半當掉", r.note)
        # 只寫前五行的人抓不到它（當掉以前印的都一樣）
        f5 = write(BASE / "five.txt", "\n".join(TEACHER.splitlines()[:5]) + "\n")
        _ctx, chk = grader.build(les, None, env=env, overrides={"lessons/1-1/expected.txt": f5}, only=spec)
        parsed = chk[0].parse()
        st, _ = chk[0].statuses(parsed.checks, parsed.marks)
        self.assertTrue(all(row["status"] == "pass" for row in st["m1"][:5]))


class OtherChecks(unittest.TestCase):
    def setUp(self):
        start()

    def test_receipt_reference_passes_and_start_does_not(self):
        self.assertFalse(ev(["receipt"]).results[0].ok)
        shutil.copy(D / "reference" / "receipt.py", L / "lessons" / LID / "receipt.py")
        r = ev(["receipt"]).results[0]
        self.assertTrue(r.ok, r.detail)

    def test_receipt_without_end_shows_the_hint(self):
        src = (D / "reference" / "receipt.py").read_text(encoding="utf-8").replace('end="："', 'end="\\n"')
        write(L / "lessons" / LID / "receipt.py", src)
        r = ev(["receipt"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("end", r.detail)

    def test_receipt_syntax_error_is_explained(self):
        src = (D / "reference" / "receipt.py").read_text(encoding="utf-8").replace('print("第 1 張")', 'print("第 1 張)')
        write(L / "lessons" / LID / "receipt.py", src)
        r = ev(["receipt"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("SyntaxError", r.detail)

    def test_guess_and_ai_answers(self):
        g = L / "lessons" / LID / "guess.txt"
        answers = iter(["B", "a", "C. 一行：「午餐120 元」（午餐後面沒有空格）", "B"])
        g.write_text("\n".join(("答：" + next(answers)) if ln.startswith("答：") else ln
                               for ln in g.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
        out = ev(["guess"])
        self.assertEqual([r.ok for r in out.results], [True, True, True, True], [r.detail for r in out.results])
        q = L / "lessons" / LID / "ai_quiz.txt"
        answers = iter(["學過", "沒有學過", "學 過"])
        q.write_text("\n".join(("答：" + next(answers)) if ln.startswith("答：") else ln
                               for ln in q.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [True, True, True], [r.detail for r in out.results])

    def test_full_run_through_check_py(self):
        """check.py 1-01（課號補 0 也認得）：猜 12、全對 13 題。"""
        home = fresh_dir("l11_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_check(["start", "1-01"], env, stdin="")
        self.assertIn("uv run check.py 1-1", r.stdout)
        work = L / "lessons" / LID
        shutil.copy(D / "reference" / "receipt.py", work / "receipt.py")
        write(work / "expected.txt", TEACHER)
        for name, ans in (("guess.txt", ["B", "A", "C", "B"]), ("ai_quiz.txt", ["學過", "沒學過", "學過"])):
            it = iter(ans)
            p = work / name
            p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                                   for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
        r = run_check(["1-01", "--predict", "12", "--no-review"], env)
        self.assertIn("13／13", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的預期輸出把 3 個壞版本全部抓到了。", r.stdout)


if __name__ == "__main__":
    unittest.main()
