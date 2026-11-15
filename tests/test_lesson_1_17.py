"""1-17〈看懂 AI 最愛的寫法（上）：推導式、zip〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 這一課新加三樣，都只對寫了它的 checks.json 生效：
  run 的 loose（比的時候空格不算：AI 照描述寫的程式，「2 筆」和「2筆」都對）、
  run 的 ast_require（convert.py 規定用推導式、或迴圈＋append 寫：cut2 = cut 直接抄答案的過不了）、
  type either（第③圈兩條路選一條：AI 照學員的白話描述寫的程式貼進 answer.py、只跑測試；沒有 AI 帳號的做 describe_quiz.txt 選擇題）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l117"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-17"
D = COURSE / "lessons" / LID
DATA = 'dates = ["11/01", "11/02", "11/03", "11/04"]\namounts = [120, 85, 300, 45]\n'
# 影片裡 AI（免費聊天版）照熊的描述寫的那種：用推導式＋zip、f-string，數字和字中間有空格
AI_CODE = ("big_days = [(d, a) for d, a in zip(dates, amounts) if a >= 100]\n"
           "for d, a in big_days:\n    print(f\"{d} {a} 元\")\n"
           "total = sum(a for d, a in big_days)\n"
           "print(f\"100 元以上的有 {len(big_days)} 筆，合計 {total} 元\")\n")


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


def res(out: grader.Outcome, rid: str) -> grader.Result:
    return next(r for r in out.results if r.id == rid)


def answer(name: str, answers: list[str]) -> None:
    p = L / "lessons" / LID / name
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def put_answer(code: str, head: str | None = None) -> None:
    """answer.py：起點檔（說明＋資料兩行）後面貼上 AI 的程式。"""
    base = (D / "start" / "answer.py").read_text(encoding="utf-8") if head is None else head
    write(L / "lessons" / LID / "answer.py", base + code)


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Whole(unittest.TestCase):
    def test_fourteen_items(self):
        les = grader.load_lesson(LID, COURSE)
        self.assertEqual(len(grader.plan(les, L)), 14)

    def test_teacher_answers_pass_everything_on_the_ai_path(self):
        start()
        for f in ("convert.py", "pairs.py"):
            shutil.copy(D / "reference" / f, L / "lessons" / LID / f)
        answer("predict.txt", ["A", "B", "C"])
        answer("short_quiz.txt", ["A", "C", "B", "C"])
        put_answer(AI_CODE)
        les = grader.load_lesson(LID, COURSE)
        out = grader.evaluate(les, L)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results if not r.ok])
        self.assertTrue(any("AI 版（answer.py）" in s for s in out.summaries), out.summaries)

    def test_start_files_pass_nothing(self):
        start()
        les = grader.load_lesson(LID, COURSE)
        out = grader.evaluate(les, L)
        self.assertEqual(out.passed, 0, [(r.id, r.detail) for r in out.results if r.ok])


class Convert(unittest.TestCase):
    def setUp(self):
        start()

    def test_reference_passes_both(self):
        shutil.copy(D / "reference" / "convert.py", L / "lessons" / LID / "convert.py")
        out = ev(["convert-1", "convert-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_copying_the_answer_is_not_a_comprehension(self):
        src = (D / "reference" / "convert.py").read_text(encoding="utf-8").replace("cut2 = [a - 20 for a in amounts]", "cut2 = cut")
        write(L / "lessons" / LID / "convert.py", src)
        r = res(ev(["convert-1"]), "convert-1")
        self.assertFalse(r.ok)
        self.assertIn("cut2 要用一行推導式寫", r.detail)

    def test_back_to_loop_must_append_in_a_for(self):
        src = (D / "reference" / "convert.py").read_text(encoding="utf-8")
        src = src.replace("small2 = []\nfor a in amounts:\n    if a < 100:\n        small2.append(a)\n", "small2 = small\n")
        write(L / "lessons" / LID / "convert.py", src)
        r = res(ev(["convert-1"]), "convert-1")
        self.assertFalse(r.ok)
        self.assertIn("改回迴圈", r.detail)

    def test_hardcoded_lists_fail_the_swap(self):
        src = (D / "reference" / "convert.py").read_text(encoding="utf-8").replace("print(cut2)", "print([100, 65, 280, 25])")
        write(L / "lessons" / LID / "convert.py", src)
        out = ev(["convert-1", "convert-2"])
        self.assertTrue(res(out, "convert-1").ok)
        self.assertFalse(res(out, "convert-2").ok)

    def test_greater_than_misses_the_100(self):
        src = (D / "reference" / "convert.py").read_text(encoding="utf-8").replace(
            "big2 = [a for a in amounts if a >= 100]", "big2 = [a for a in amounts if a > 100]").replace(
            "    if a >= 100:\n        big.append(a)", "    if a > 100:\n        big.append(a)")
        write(L / "lessons" / LID / "convert.py", src)
        out = ev(["convert-1", "convert-2"])
        self.assertTrue(res(out, "convert-1").ok)   # 原本的金額沒有剛好 100
        self.assertFalse(res(out, "convert-2").ok)  # 換掉以後有 100


class Pairs(unittest.TestCase):
    def setUp(self):
        start()

    def test_reference_passes_both(self):
        shutil.copy(D / "reference" / "pairs.py", L / "lessons" / LID / "pairs.py")
        out = ev(["pairs-1", "pairs-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_spaces_do_not_matter(self):
        write(L / "lessons" / LID / "pairs.py", DATA + "for d, a in zip(dates, amounts):\n    print(f\"{d}  {a}元\")\n")
        out = ev(["pairs-1", "pairs-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_hardcoded_dates_fail_the_swap(self):
        write(L / "lessons" / LID / "pairs.py", DATA + "print('11/01 120 元')\nprint('11/02 85 元')\nprint('11/03 300 元')\nprint('11/04 45 元')\n")
        out = ev(["pairs-1", "pairs-2"])
        self.assertTrue(res(out, "pairs-1").ok)
        self.assertFalse(res(out, "pairs-2").ok)


class Either(unittest.TestCase):
    def setUp(self):
        start()

    def test_ai_code_passes(self):
        put_answer(AI_CODE)
        out = ev(["r3"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual([r.id for r in out.results], ["r3-1", "r3-2", "r3-3"])

    def test_reference_answer_passes(self):
        shutil.copy(D / "reference" / "answer.py", L / "lessons" / LID / "answer.py")
        self.assertTrue(all(r.ok for r in ev(["r3"]).results))

    def test_copying_report_py_passes_too(self):
        # check 只跑測試（總企劃 1-17）：照抄 report.py 也會過，README 寫明這一圈練的是描述
        shutil.copy(D / "start" / "report.py", L / "lessons" / LID / "answer.py")
        self.assertTrue(all(r.ok for r in ev(["r3"]).results))

    def test_greater_than_fails_on_exactly_100(self):
        put_answer(AI_CODE.replace(">= 100", "> 100"))
        out = ev(["r3"])
        self.assertEqual([r.ok for r in out.results], [True, False, True])
        self.assertIn("100 也算", res(out, "r3-2").detail)

    def test_ai_redefines_the_data(self):
        put_answer(DATA + AI_CODE)
        out = ev(["r3"])
        self.assertTrue(res(out, "r3-1").ok)
        self.assertFalse(res(out, "r3-2").ok)
        self.assertIn("把那兩行刪掉", res(out, "r3-2").detail)

    def test_different_wording_fails(self):
        put_answer(AI_CODE.replace("100 元以上的有", "超過 100 元的有"))
        out = ev(["r3"])
        self.assertFalse(any(r.ok for r in out.results))

    def test_quiz_path(self):
        answer("describe_quiz.txt", ["A", "C", "B"])
        out = ev(["r3"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertTrue(any("選擇題版" in s for s in out.summaries), out.summaries)

    def test_quiz_path_one_wrong(self):
        answer("describe_quiz.txt", ["A", "B", "B"])
        out = ev(["r3"])
        self.assertEqual([r.ok for r in out.results], [True, False, True])
        self.assertIn("不對", res(out, "r3-2").detail)

    def test_quiz_two_letters_is_not_a_choice(self):
        answer("describe_quiz.txt", ["A", "B 或 C", "B"])
        r = res(ev(["r3"]), "r3-2")
        self.assertFalse(r.ok)
        self.assertIn("只能選一個", r.detail)

    def test_neither_started(self):
        out = ev(["r3"])
        self.assertFalse(any(r.ok for r in out.results))
        self.assertIn("兩條選一條", out.results[0].detail)

    def test_both_started_takes_the_one_that_passes(self):
        put_answer("print('還沒好')\n")
        answer("describe_quiz.txt", ["A", "C", "B"])
        out = ev(["r3"])
        self.assertTrue(all(r.ok for r in out.results))

    def test_both_started_neither_passes_takes_more_passes(self):
        put_answer(AI_CODE.replace(">= 100", "> 100"))   # 2 題過
        answer("describe_quiz.txt", ["B", "B", "A"])      # 0 題過
        out = ev(["r3"])
        self.assertEqual([r.ok for r in out.results], [True, False, True])

    def test_missing_answer_file_uses_the_quiz(self):
        (L / "lessons" / LID / "answer.py").unlink()
        answer("describe_quiz.txt", ["A", "C", "B"])
        self.assertTrue(all(r.ok for r in ev(["r3"]).results))


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_predict_and_short_quiz(self):
        answer("predict.txt", ["A", "B", "C"])
        answer("short_quiz.txt", ["A", "C", "B", "C"])
        out = ev(["predict", "short"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_common_mistakes(self):
        answer("predict.txt", ["C", "C", "A"])        # 以為是加總、以為會變 True／False、以為 zip 會配滿
        answer("short_quiz.txt", ["B", "A", "A", "A"])  # 以為 d 是編號、a - 20 放 for、zip 配到 11/04、enumerate 從 0
        out = ev(["predict", "short"])
        self.assertFalse(any(r.ok for r in out.results))


if __name__ == "__main__":
    unittest.main()
