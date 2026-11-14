"""1-4〈數字與運算：分帳的零頭〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

重點是第③圈 cases 模式的兩個新旗標（只對寫了它的 checks.json 生效，1-3 不受影響）：
  input_type "int"：左邊是整數金額（不加引號）；
  expect_ints 3：右邊是三個人各付多少「334, 333, 333」，check 把 split3() 交回的 (334, 333, 333) 當 list 比，每個數字的型別也比。
三個壞版本：用 round 的（1000 → 333×3）、零頭全給第一個人（1001 → 335, 333, 333）、用 int(total / 3) 的（退款 -1000 → -332, -332, -333）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l14"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-4"
D = COURSE / "lessons" / LID
TEACHER = (D / "answers" / "cases.txt").read_text(encoding="utf-8")
BEAR4 = "1000 -> 334, 333, 333\n999 -> 333, 333, 333\n1001 -> 334, 334, 333\n2 -> 1, 1, 0\n"   # 影片裡熊的四組：沒有退款


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


def cases(text: str) -> grader.Outcome:
    write(L / "lessons" / LID / "cases.txt", text)
    return ev(["r3"])


def answer(name: str, answers: list[str]) -> None:
    p = L / "lessons" / LID / name
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Cases(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_answer_catches_all_three_versions(self):
        out = cases(TEACHER)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 2 行抓到")   # round：1000 → 333, 333, 333
        self.assertEqual(part(out, "m2").note, "被第 3 行抓到")   # 零頭全給第一個人：1001 → 335, 333, 333
        self.assertEqual(part(out, "m3").note, "被第 5 行抓到")   # int(total / 3)：-1000 → -332, -332, -333
        self.assertIn("你的案例把 3 個壞版本全部抓到了。", out.summaries)

    def test_start_file_is_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你寫了 1 組案例，這課要至少 4 組", part(out, "count").detail)
        self.assertTrue(part(out, "wheat").ok)   # 範例那一行在正確版上是對的
        self.assertTrue(part(out, "m1").ok)      # 1000 就抓得到 round 那一版

    def test_bear_four_cases_without_a_refund_let_the_negative_version_slip(self):
        out = cases(BEAR4)
        self.assertTrue(part(out, "count").ok and part(out, "wheat").ok)
        self.assertTrue(part(out, "m1").ok and part(out, "m2").ok)
        self.assertEqual(part(out, "m2").note, "被第 3 行抓到")
        self.assertFalse(part(out, "m3").ok)
        self.assertIn("退款（負數）", part(out, "m3").detail)
        self.assertIn("你的案例抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)
        self.assertIn("  ・退款（負數）的金額，像 -1000", out.summaries)

    def test_only_multiples_of_three_let_round_slip(self):
        out = cases("999 -> 333, 333, 333\n900 -> 300, 300, 300\n3 -> 1, 1, 1\n0 -> 0, 0, 0\n")
        self.assertTrue(part(out, "wheat").ok)
        self.assertFalse(part(out, "m1").ok)
        self.assertIn("除不盡的金額", part(out, "m1").detail)

    def test_wrong_order_or_wrong_refund_shows_what_the_reference_computes(self):
        out = cases("1000 -> 333, 333, 334\n")
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn("split3(1000) 正確版算出來是 334, 333, 333，你寫的是 333, 333, 334", r.detail)
        self.assertIn("零頭從第一個人開始", r.detail)
        out = cases("-1000 -> -334, -333, -333\n")   # 以為零頭是 -1：其實 -1000 // 3 是 -334、-1000 % 3 是 2
        self.assertIn("正確版算出來是 -333, -333, -334", part(out, "wheat").detail)

    def test_list_parentheses_and_ideographic_comma_are_fine(self):
        out = cases("1000 -> [334, 333, 333]\n1001 -> (334, 334, 333)\n999 -> 333、333、333\n-1000 -> -333,-333,-334\n")
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_float_on_the_right_is_not_an_integer(self):
        out = cases("999 -> 333.0, 333.0, 333.0\n")
        self.assertFalse(part(out, "count").ok)
        self.assertIn("每個人付的都要是整數元", part(out, "count").detail)

    def test_beginner_mistakes_get_plain_messages(self):
        for text, want in (("1000 334, 333, 333\n", "少了箭頭"),
                           ('"1000" -> 334, 333, 333\n', "有引號，是文字"),
                           ("1000.5 -> 334, 333, 333\n", "有小數點"),
                           ("1000 -> 334 333 333\n", "中間用逗號隔開"),
                           ("1000 -> 334元, 333元, 333元\n", "不要寫「元」"),
                           ("1000 -> 334, 333\n", "寫了 2 個數字"),
                           ("1000 -> 334\n", "寫了 1 個數字"),
                           ("「1000」 -> 334, 333, 333\n", "中文的引號")):
            out = cases(text)
            self.assertFalse(any(r.ok for r in out.results), text)
            self.assertIn(want, part(out, "count").detail, text)

    def test_crlf_fullwidth_arrow_and_comments_are_fine(self):
        out = cases(("# 我的案例\n\n" + TEACHER.replace("1001 ->", "1001 →") + "\n# 寫完了\n").replace("\n", "\r\n"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class OtherChecks(unittest.TestCase):
    def setUp(self):
        start()

    def test_split_reference_passes_and_start_does_not(self):
        r = ev(["split"]).results[0]
        self.assertFalse(r.ok)
        shutil.copy(D / "reference" / "split.py", L / "lessons" / LID / "split.py")
        r = ev(["split"]).results[0]
        self.assertTrue(r.ok, r.detail)

    def test_split_with_slash_prints_a_float_and_shows_the_hint(self):
        src = (D / "reference" / "split.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "split.py", src.replace("each = total // people", "each = total / people"))
        r = ev(["split"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("362.5", r.detail)
        self.assertIn("each 用 //", r.detail)

    def test_guess_answers_accept_fullwidth_and_unicode_minus(self):
        answer("guess.txt", ["3", "2", "－4", "3", "81", "4", "−25"])
        out = ev(["guess"])
        self.assertEqual([r.ok for r in out.results], [True] * 7, [r.detail for r in out.results])
        answer("guess.txt", ["3.4", "2", "-3", "-2", "12", "24", "9"])
        out = ev(["guess"])
        self.assertEqual([r.ok for r in out.results], [False, True, False, False, False, False, False])
        self.assertIn("比較小的那邊", out.results[2].detail)

    def test_ai_list_answers(self):
        answer("ai_list.txt", ["A", "b", "A. 要寫進需求卡", "C"])
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [True] * 4, [r.detail for r in out.results])

    def test_full_run_through_check_py(self):
        """check.py 1-04（課號補 0 也認得）：全對 17 題。"""
        home = fresh_dir("l14_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_check(["start", "1-04"], env, stdin="")
        self.assertIn("uv run check.py 1-4", r.stdout)
        work = L / "lessons" / LID
        shutil.copy(D / "reference" / "split.py", work / "split.py")
        write(work / "cases.txt", TEACHER)
        answer("guess.txt", ["3", "2", "-4", "3", "81", "4", "-25"])
        answer("ai_list.txt", ["A", "B", "A", "C"])
        r = run_check(["1-04", "--predict", "16", "--no-review"], env)
        self.assertIn("17／17", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的案例把 3 個壞版本全部抓到了。", r.stdout)


if __name__ == "__main__":
    unittest.main()
