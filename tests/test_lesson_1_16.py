"""1-16〈可變與參照：為什麼你的 list 自己變了〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

這一課沒有改 grader／runner，用到的都是前幾課已有的：answers（strict_choice、每題自己的 choices）、run 的 swap（1-C1）、chaff 的 assert 模式（1-8）。
第③圈「先寫 assert 證明它錯，再修好」：chaff 的 module 是 budget，學員的 assert 拿去跑課程的正確版和 3 個算錯的版本
（m1 就是學員拿到的 budget.py：nov、dec 都直接等於 fixed；m2 只有 nov 複製、機票加進 fixed；m3 只有 dec 複製、午餐先加進 fixed），
再跑學員修好的 budget.py（swap 把 fixed 換掉：把數字再打一次的過不了），最後跑學員自己的 checks_budget.py（在自己的 budget.py 上要全部成立）。
影片裡熊寫的是「固定開銷還是 12499」，一條就把三個都抓到；只檢查 11 月的合計只抓得到 m1；思考站的 A、C 在原本的 budget.py 上成立，證明不了它錯。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l116"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-16"
D = COURSE / "lessons" / LID
IMP = "from budget import fixed, nov, dec\n"
BEAR = IMP + "# 固定開銷還是 12000 加 499\nassert sum(fixed) == 12499\n"   # 影片裡熊寫的那一條
FIXED = (D / "reference" / "budget.py").read_text(encoding="utf-8")


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
    """r3 的 count、wheat、m1…（照 1-14：id 最後一段）；budget-1、green 這種就照整個 id。"""
    return next(r for r in out.results if r.id == suffix or (r.id.startswith("r3") and r.id.rsplit("-", 1)[-1] == suffix))


def r3(text: str) -> grader.Outcome:
    write(L / "lessons" / LID / "checks_budget.py", text)
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


class Asserts(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_checks_catch_all_three(self):
        out = r3((D / "answers" / "checks_budget.py").read_text(encoding="utf-8"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_bear_one_line_catches_all_three(self):
        """影片裡熊的一條：固定開銷還是 12499。三個算錯的版本都改到了 fixed。"""
        out = r3(BEAR)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 3 行抓到")

    def test_only_november_catches_only_the_original(self):
        out = r3(IMP + "assert sum(nov) == 12619\n")
        self.assertTrue(part(out, "count").ok and part(out, "wheat").ok, [(r.id, r.detail) for r in out.results])
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, False, False])
        self.assertIn("固定開銷 fixed 本身有沒有被改到？", part(out, "m2").detail)
        self.assertIn("你的檢查抓到 1 個壞版本，還有 2 個溜過去：", out.summaries)

    def test_station_options_a_and_c_do_not_prove_it(self):
        """思考站：A（兩個月一樣多）在原本的 budget.py 上成立、在正確版上反而不成立；C（大於 12000）兩邊都成立。"""
        a = r3(IMP + "assert sum(nov) == sum(dec)\n")
        self.assertFalse(part(a, "wheat").ok)
        self.assertFalse(part(a, "m1").ok)
        c = r3(IMP + "assert sum(nov) > 12000\n")
        self.assertTrue(part(c, "wheat").ok)
        self.assertEqual([part(c, m).ok for m in ("m1", "m2", "m3")], [False, False, False])

    def test_wrong_arithmetic_fails_on_the_reference(self):
        out = r3(IMP + "assert sum(fixed) == 12500\n")
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("12499", part(out, "wheat").detail)

    def test_start_file_needs_one(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)


class Fix(unittest.TestCase):
    """第③圈的第二步：修好 budget.py；修好以後學員自己的 checks_budget.py 要全部成立。"""

    def setUp(self):
        start()

    def test_proof_first_then_fix(self):
        write(L / "lessons" / LID / "checks_budget.py", BEAR)
        out = ev(["r3", "budget-1", "budget-2", "green"])
        self.assertTrue(all(part(out, k).ok for k in ("count", "wheat", "m1", "m2", "m3")))
        self.assertEqual([part(out, k).ok for k in ("budget-1", "budget-2", "green")], [False, False, False])
        self.assertIn("AssertionError", part(out, "green").detail)
        write(L / "lessons" / LID / "budget.py", FIXED)
        out = ev(["budget-1", "budget-2", "green"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_slice_fix_also_passes(self):
        src = (L / "lessons" / LID / "budget.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "budget.py", src.replace("nov = fixed\n", "nov = fixed[:]\n").replace("dec = fixed\n", "dec = fixed[:]\n"))
        out = ev(["budget-1", "budget-2"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_half_fix_is_caught(self):
        """只改 dec 那一行（m3 的寫法）：12 月和固定開銷還是錯的。只改 nov（m2）：兩個月對了，固定開銷錯。"""
        src = (L / "lessons" / LID / "budget.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "budget.py", src.replace("dec = fixed\n", "dec = fixed.copy()\n"))
        self.assertFalse(ev(["budget-1"]).results[0].ok)
        write(L / "lessons" / LID / "budget.py", src.replace("nov = fixed\n", "nov = fixed.copy()\n"))
        out = ev(["budget-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("固定開銷 15499 元", out.results[0].detail)

    def test_retyped_numbers_fail_the_swap(self):
        src = (L / "lessons" / LID / "budget.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "budget.py", src.replace("nov = fixed\n", "nov = [12000, 499]\n").replace("dec = fixed\n", "dec = [12000, 499]\n"))
        out = ev(["budget-1", "budget-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])

    def test_green_needs_their_own_assert_to_hold(self):
        write(L / "lessons" / LID / "budget.py", FIXED)
        write(L / "lessons" / LID / "checks_budget.py", IMP + "assert sum(nov) == 15619\n")   # 照錯的版本寫的答案
        self.assertFalse(ev(["green"]).results[0].ok)


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_predict_and_final_a(self):
        answer("predict.txt", ["5", "C", "A"])
        answer("final_a.txt", ["B", "A", "C", "B"])
        out = ev(["predict", "final"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_common_mistakes(self):
        answer("predict.txt", ["6", "A", "B"])
        answer("final_a.txt", ["A", "B", "A", "A"])
        out = ev(["predict", "final"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_two_letters_is_not_a_choice(self):
        answer("final_a.txt", ["A 或 B", "A", "C", "B"])
        out = ev(["final"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("只能選一個", out.results[0].detail)


class Programs(unittest.TestCase):
    def setUp(self):
        start()

    def test_references_pass_and_starts_do_not(self):
        ids = ["ids-1", "ids-2", "ledgers-1", "ledgers-2"]
        out = ev(ids)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        for f in ("ids.py", "ledgers.py"):
            shutil.copy(D / "reference" / f, L / "lessons" / LID / f)
        out = ev(ids)
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_hardcoded_ids_fail_the_swap(self):
        write(L / "lessons" / LID / "ids.py", "a = [120, 85]\nb = a\nc = a.copy()\nprint(True)\nprint(False)\nprint(True)\n")
        out = ev(["ids-1", "ids-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])

    def test_equals_instead_of_is_fails(self):
        write(L / "lessons" / LID / "ids.py", "a = [120, 85]\nb = a\nc = a.copy()\nprint(a == b)\nprint(a == c)\nprint(a == c)\n")
        self.assertFalse(ev(["ids-1"]).results[0].ok)

    def test_new_empty_lists_also_pass(self):
        src = (L / "lessons" / LID / "ledgers.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "ledgers.py", src.replace("bear = start\n", "bear = []\n").replace("rabbit = start\n", "rabbit = []\n"))
        out = ev(["ledgers-1", "ledgers-2"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_shared_ledger_prints_both(self):
        out = ev(["ledgers-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("[120, 300]", out.results[0].detail)


if __name__ == "__main__":
    unittest.main()
