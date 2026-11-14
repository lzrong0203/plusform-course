"""1-3〈資料型別：int、float、str、bool、None〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

重點是第③圈的 chaff 新模式 cases（學員寫案例表「"120" -> 120」，check 把左邊丟進課程的 to_yuan()，
跟正確版與 3 個壞版本比，連型別一起比：120、120.0、"120" 都不同），和特殊作答「# 已知會當掉」。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l13"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-3"
D = COURSE / "lessons" / LID
TEACHER = (D / "answers" / "cases.txt").read_text(encoding="utf-8")
FOUR = '"120" -> 120\n"85元" -> 85\n"1,200" -> 1200\n" 35 " -> 35\n'


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

    def test_teacher_answer_catches_all_three_versions_and_the_crash_mark_counts(self):
        out = cases(TEACHER)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 2 行抓到")   # "120" 交回文字 "120"
        self.assertEqual(part(out, "m2").note, "被第 3 行抓到")   # "85元" 變成 85.0
        self.assertEqual(part(out, "m3").note, "被第 4 行抓到")   # "1,200" 當掉
        marks = [r for r in out.results if r.special]
        self.assertEqual(len(marks), 1)
        self.assertIn("國字的一百", marks[0].note)
        self.assertIn("你的案例把 3 個壞版本全部抓到了。", out.summaries)

    def test_start_file_is_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你寫了 1 組案例，這課要至少 4 組", part(out, "count").detail)
        self.assertTrue(part(out, "wheat").ok)   # 範例那一行在正確版上是對的
        self.assertFalse(part(out, "smin").ok)
        self.assertIn("# 已知會當掉", part(out, "smin").detail)

    def test_without_a_comma_case_the_comma_version_slips_through_with_a_hint(self):
        out = cases('"120" -> 120\n"85元" -> 85\n" 35 " -> 35\n"0" -> 0\n')
        self.assertTrue(part(out, "m1").ok and part(out, "m2").ok)
        self.assertFalse(part(out, "m3").ok)
        self.assertIn("千分位逗號", part(out, "m3").detail)
        self.assertIn("你的案例抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)
        self.assertFalse(part(out, "smin").ok)

    def test_text_or_float_on_the_right_is_a_type_mismatch(self):
        for right, shown in (('"120"', '"120"（文字 str）'), ("120.0", "120.0（小數 float）")):
            out = cases(f'"120" -> {right}\n')
            r = part(out, "wheat")
            self.assertFalse(r.ok)
            self.assertIn("正確版變成 120（整數 int）", r.detail)
            self.assertIn(f"你寫的是 {shown}", r.detail)
            self.assertIn("型別不一樣", r.detail)

    def test_true_is_not_one(self):
        out = cases('"1" -> True\n')
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("True（布林 bool）", part(out, "wheat").detail)

    def test_reference_crash_without_a_mark_suggests_the_mark(self):
        out = cases(FOUR + '"一百" -> 100\n')
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn('to_yuan("一百") 連正確版都會當掉', r.detail)
        self.assertIn("ValueError", r.detail)
        self.assertIn("# 已知會當掉", r.detail)

    def test_crash_mark_on_an_amount_the_reference_can_convert_is_wrong(self):
        out = cases(FOUR + '"60"  # 已知會當掉\n')
        mk = next(r for r in out.results if r.special)
        self.assertFalse(mk.ok)
        self.assertIn("正確版轉得出來", mk.detail)
        self.assertIn("60（整數 int）", mk.detail)
        self.assertNotIn("smin", [r.id.rsplit("-", 1)[-1] for r in out.results])

    def test_crash_mark_with_question_mark_and_other_crashes(self):
        for line in ('"12.5" -> ？  # 已知會當掉', '"abc"#已知會當掉', '"" -> # 已知會當掉'):
            out = cases(FOUR + line + "\n")
            self.assertTrue(all(r.ok for r in out.results), (line, [(r.id, r.detail) for r in out.results]))

    def test_negative_refund_can_be_marked_as_a_requirement_problem(self):
        out = cases(FOUR + '"-35" -> -35  # 需求有問題\n' + '"一百"  # 已知會當掉\n')
        specials = [r for r in out.results if r.special]
        self.assertEqual([r.ok for r in specials], [True, True], [r.detail for r in specials])
        self.assertIn("退款", specials[0].note)

    def test_hash_inside_quotes_arrows_and_fullwidth(self):
        text = '"120" → 120\n"85元"=>85\n"1,200"－＞1200\n" # 35 " -> 0  # 這行左邊的 # 在引號裡\n'
        out = cases(text)
        self.assertEqual(part(out, "count").detail, "", part(out, "count").detail)
        self.assertIn('to_yuan(" # 35 ") 連正確版都會當掉', part(out, "wheat").detail)

    def test_beginner_mistakes_get_plain_messages(self):
        for text, want in (('"120" 120\n', "少了箭頭"),
                           ("120 -> 120\n", "沒有引號，是數字"),
                           ("「120」 -> 120\n", "中文的引號"),
                           ('"120" -> 120元\n', "不要寫單位"),
                           ('“120” -> 120\n', "中文的引號")):
            out = cases(text)
            self.assertFalse(any(r.ok for r in out.results), text)
            self.assertIn(want, part(out, "count").detail, text)

    def test_crlf_and_comments_are_fine(self):
        out = cases(("# 我的案例\n\n" + TEACHER + "\n# 寫完了\n").replace("\n", "\r\n"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class OtherChecks(unittest.TestCase):
    def setUp(self):
        start()

    def test_entry_reference_passes_and_start_does_not(self):
        out = ev(["entry-amount", "entry-note", "entry-receipt"])
        self.assertFalse(any(r.ok for r in out.results))
        shutil.copy(D / "reference" / "entry.py", L / "lessons" / LID / "entry.py")
        out = ev(["entry-amount", "entry-note", "entry-receipt"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_entry_amount_as_text_shows_the_hint(self):
        src = (D / "reference" / "entry.py").read_text(encoding="utf-8")
        for bad, rid, hint in (("amount = \"120\"", "entry-amount", "不加引號"), ("amount = 120.0", "entry-amount", "小數點"),
                               ("receipt = \"None\"", "entry-receipt", "加了引號就變成文字")):
            key = bad.split(" = ")[0] + " = "
            line = next(ln for ln in src.splitlines() if ln.startswith(key))
            write(L / "lessons" / LID / "entry.py", src.replace(line, bad))
            r = ev([rid]).results[0]
            self.assertFalse(r.ok, bad)
            self.assertIn(hint, r.detail, bad)

    def test_types_answers_accept_the_full_class_text(self):
        answer("types.txt", ["<class 'float'>", "str", "Bool", "int"])
        out = ev(["types"])
        self.assertEqual([r.ok for r in out.results], [True, True, True, True], [r.detail for r in out.results])
        answer("types.txt", ["int", "int", "str", "None"])
        out = ev(["types"])
        self.assertEqual([r.ok for r in out.results], [False, False, False, False])

    def test_full_run_through_check_py(self):
        """check.py 1-03（課號補 0 也認得）：猜 11、全對 13 題。"""
        home = fresh_dir("l13_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_check(["start", "1-03"], env, stdin="")
        self.assertIn("uv run check.py 1-3", r.stdout)
        work = L / "lessons" / LID
        shutil.copy(D / "reference" / "entry.py", work / "entry.py")
        write(work / "cases.txt", TEACHER)
        answer("types.txt", ["float", "str", "bool", "int"])
        r = run_check(["1-03", "--predict", "11", "--no-review"], env)
        self.assertIn("13／13", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的案例把 3 個壞版本全部抓到了。", r.stdout)


if __name__ == "__main__":
    unittest.main()
