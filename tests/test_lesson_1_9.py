"""1-9〈if／elif／else：預算燈號與 BMI〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

第①圈：budget_light.py（官方測試，check 餵四組邊界：花 500、800、1000、1001，預算 1000）、trace.txt 追蹤 4 題；
第②圈：ai_review.txt 判讀家教真的回的 6 則建議（2026-11-15 示範帳號實錄）；
第③圈：checks_bmi.py 替課程的 bmi_level() 寫 assert（chaff 的 assert 模式，1-8 起），分級照國健署〈成人健康體位標準〉原文：
  體重過輕（<18.5）、健康體重（18.5≤BMI<24）、體重過重（24≤BMI<27）、肥胖（≥27）。
三個壞版本：m1 24 的邊界把 >= 寫成 >（剛好 24 才抓得到，這課的主角）、m2 18.5 的邊界把 >= 寫成 >、m3 elif 順序寫反（體重過重永遠不會出現）。
特殊作答（# 已知會當掉、# 需求有問題）這課有開（answers/special.json，選做），完整流程在 test_flow.py。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import copy
import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l19"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-9"
D = COURSE / "lessons" / LID
HEAD = "from bmi import bmi_level\n\n"
# 影片裡熊的六條：測了 18.5 和 27 兩個邊界，偏偏漏了中間的 24
BEAR = ['assert bmi_level(16) == "體重過輕"', 'assert bmi_level(18.5) == "健康體重"', 'assert bmi_level(22) == "健康體重"',
        'assert bmi_level(25) == "體重過重"', 'assert bmi_level(27) == "肥胖"', 'assert bmi_level(30) == "肥胖"']
AI_OK = ["不採用", "採用", "採用", "要查證", "要查證", "不採用"]


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


def ev(ids: list[str], ledger: Path | None = L, tweak=None) -> grader.Outcome:
    les = grader.load_lesson(LID, COURSE)
    only = [copy.deepcopy(c) for c in les.checks if c["id"] in ids]
    if tweak:
        for c in only:
            tweak(c)
    return grader.evaluate(les, ledger, only=only)


def part(out: grader.Outcome, suffix: str) -> grader.Result:
    return next(r for r in out.results if r.id.rsplit("-", 1)[-1] == suffix)


def r3(lines: list[str], head: str = HEAD) -> grader.Outcome:
    write(L / "lessons" / LID / "checks_bmi.py", head + "\n".join(lines) + "\n")
    return ev(["r3"])


def answer(name: str, answers: list[str]) -> None:
    p = L / "lessons" / LID / name
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def light(src: str) -> grader.Outcome:
    write(L / "lessons" / LID / "budget_light.py", src)
    return ev(["light-1", "light-2", "light-3", "light-4"])


REF_LIGHT = (D / "reference" / "budget_light.py").read_text(encoding="utf-8")


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Asserts(unittest.TestCase):
    def setUp(self):
        start()

    def test_labels_follow_the_official_standard(self):
        """正確版照國健署原文：<18.5 體重過輕、18.5≤BMI<24 健康體重、24≤BMI<27 體重過重、≥27 肥胖（rec/src/hpa_adult_bmi_standard.txt）。"""
        ns: dict = {}
        exec(compile((D / "reference" / "bmi.py").read_text(encoding="utf-8"), "bmi.py", "exec"), ns)
        f = ns["bmi_level"]
        got = {x: f(x) for x in (16, 18.4, 18.5, 23.9, 24, 26.9, 27, 35)}
        self.assertEqual(got, {16: "體重過輕", 18.4: "體重過輕", 18.5: "健康體重", 23.9: "健康體重", 24: "體重過重",
                               26.9: "體重過重", 27: "肥胖", 35: "肥胖"})
        self.assertEqual((D / "start" / "bmi.py").read_text(encoding="utf-8").split("def bmi_level", 1)[1],
                         (D / "reference" / "bmi.py").read_text(encoding="utf-8").split("def bmi_level", 1)[1])

    def test_teacher_asserts_catch_all_three(self):
        write(L / "lessons" / LID / "checks_bmi.py", (D / "answers" / "checks_bmi.py").read_text(encoding="utf-8"))
        out = ev(["r3"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 7 行抓到")   # bmi_level(24)
        self.assertEqual(part(out, "m2").note, "被第 5 行抓到")   # bmi_level(18.5)
        self.assertEqual(part(out, "m3").note, "被第 7 行抓到")   # 24 在 m3 是健康體重
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_bear_six_let_the_24_boundary_slip(self):
        out = r3(BEAR)
        self.assertTrue(part(out, "count").ok)
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
        self.assertFalse(part(out, "m1").ok)
        self.assertIn("邊界 24", part(out, "m1").detail)
        self.assertTrue(part(out, "m2").ok)
        self.assertEqual(part(out, "m2").note, "被第 4 行抓到")   # 18.5
        self.assertTrue(part(out, "m3").ok)
        self.assertEqual(part(out, "m3").note, "被第 6 行抓到")   # 25 在 m3 是健康體重
        self.assertIn("你的檢查抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)
        for line in out.summaries:   # 每行壓在 68 欄內（VHS 錄影 70 欄）
            self.assertLessEqual(sum(2 if ord(ch) > 0x2E7F else 1 for ch in line), 68, line)

    def test_adding_24_catches_m1(self):
        out = r3(BEAR + ['assert bmi_level(24) == "體重過重"'])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 9 行抓到")

    def test_24_written_as_healthy_is_wrong_on_reference(self):
        out = r3(BEAR[:5] + ['assert bmi_level(24) == "健康體重"'])
        self.assertFalse(part(out, "wheat").ok)
        d = part(out, "wheat").detail
        self.assertIn("第 8 行", d)
        self.assertIn("體重過重", d)

    def test_old_short_label_is_wrong_on_reference(self):
        out = r3(BEAR[:5] + ['assert bmi_level(22) == "正常"'])
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("健康體重", part(out, "wheat").detail)

    def test_start_file_is_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你寫了 1 條檢查，這課要至少 6 條", part(out, "count").detail)
        self.assertTrue(part(out, "wheat").ok)   # 起點檔的範例在正確版上成立
        self.assertFalse(part(out, "m1").ok)
        self.assertIn("先寫滿 6 條檢查", part(out, "m1").detail)

    def test_only_middle_values_catch_only_the_order_mutant(self):
        out = r3(['assert bmi_level(16) == "體重過輕"', 'assert bmi_level(20) == "健康體重"', 'assert bmi_level(22) == "健康體重"',
                  'assert bmi_level(25) == "體重過重"', 'assert bmi_level(26) == "體重過重"', 'assert bmi_level(30) == "肥胖"'])
        self.assertFalse(part(out, "m1").ok)
        self.assertFalse(part(out, "m2").ok)
        self.assertTrue(part(out, "m3").ok)

    def test_marks_are_graded(self):
        out = r3(BEAR + ['assert bmi_level(24) == "體重過重"', 'assert bmi_level(-5) == "體重過輕"  # 需求有問題'])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertTrue(any(getattr(r, "special", False) for r in out.results))


class FirstRing(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_fails_reference_passes(self):
        self.assertFalse(any(r.ok for r in ev(["light-1", "light-2", "light-3", "light-4"]).results))
        out = light(REF_LIGHT)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_descending_order_also_passes(self):
        """從紅燈往下寫（> 1、>= 0.8、else）也對：題目只看印出來的燈號。"""
        body = REF_LIGHT.split("if ratio", 1)[0] + 'if ratio > 1:\n    print("紅燈")\nelif ratio >= 0.8:\n    print("黃燈")\nelse:\n    print("綠燈")\n'
        out = light(body)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_rabbit_wrong_order_is_always_green(self):
        """果凍兔（影片）：照「每個燈從哪裡開始」寫，綠燈 >= 0 寫在最前面 → 永遠綠燈；第一個沒過的是剛好 80%。"""
        body = REF_LIGHT.split("if ratio", 1)[0] + 'if ratio >= 0:\n    print("綠燈")\nelif ratio >= 0.8:\n    print("黃燈")\nelif ratio > 1:\n    print("紅燈")\n'
        out = light(body)
        self.assertEqual([r.ok for r in out.results], [True, False, False, False])
        self.assertIn("elif 的順序", part(out, "4").detail)

    def test_less_equal_at_80_fails_exact_80(self):
        out = light(REF_LIGHT.replace("ratio < 0.8", "ratio <= 0.8"))
        self.assertEqual([r.ok for r in out.results], [True, False, True, True])
        self.assertIn("剛好 80%", part(out, "2").detail)

    def test_less_than_1_fails_exact_100(self):
        out = light(REF_LIGHT.replace("ratio <= 1", "ratio < 1"))
        self.assertEqual([r.ok for r in out.results], [True, True, False, True])

    def test_two_ifs_print_two_lights(self):
        """elif 寫成兩個獨立的 if：花 500 會同時印綠燈和黃燈（expect_not_contains 抓到）。"""
        out = light(REF_LIGHT.replace("elif ratio <= 1:", "if ratio <= 1:"))
        self.assertFalse(part(out, "1").ok)

    def test_trace_answers(self):
        answer("trace.txt", ["體重過輕", " 健康體重", "「體重過重」", "肥胖"])
        out = ev(["trace"])
        self.assertEqual([r.ok for r in out.results], [True] * 4, [r.detail for r in out.results])
        answer("trace.txt", ["過輕", "正常", "健康體重", "體重過重"])
        self.assertEqual([r.ok for r in ev(["trace"]).results], [False] * 4)


class SecondRing(unittest.TestCase):
    def setUp(self):
        start()

    def test_ai_review_answers(self):
        answer("ai_review.txt", AI_OK)
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [True] * 6, [r.detail for r in out.results])
        answer("ai_review.txt", ["先不採用", "採用", "採用", "不採用", "查證", "不用"])
        self.assertEqual([r.ok for r in ev(["ai"]).results], [True] * 6)
        answer("ai_review.txt", ["採用", "不採用", "不採用", "採用", "採用", "採用"])
        self.assertEqual([r.ok for r in ev(["ai"]).results], [False] * 6)

    def test_ai_review_quotes_the_recorded_tutor(self):
        """作答檔的 6 則是示範帳號真的回的話（rec/w03_browse_transcript.json），不是編的。"""
        txt = (D / "start" / "ai_review.txt").read_text(encoding="utf-8")
        for s in ("把每個燈號和它的門檻，一起放進一個清單（或字典）裡", "那 799、801、1001 呢？", "有沒有辦法讓這些數字有個一看就懂的名字？",
                  "浮點數的除法和比較有時會有微小誤差", "如果使用者輸入 abc 或 850.5", "這件事包起來的語法？"):
            self.assertIn(s, txt)


class FullRun(unittest.TestCase):
    def test_full_run_through_check_py(self):
        """check.py 1-09（課號補 0 也認得）：全對 19 題。"""
        home = fresh_dir("l19_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        start()
        r = run_check(["start", "1-09"], env, stdin="")
        self.assertIn("uv run check.py 1-9", r.stdout)
        work = L / "lessons" / LID
        self.assertTrue((work / "bmi.py").is_file())
        shutil.copy(D / "reference" / "budget_light.py", work / "budget_light.py")
        shutil.copy(D / "answers" / "checks_bmi.py", work / "checks_bmi.py")
        answer("trace.txt", ["體重過輕", "健康體重", "體重過重", "肥胖"])
        answer("ai_review.txt", AI_OK)
        r = run_check(["1-09", "--predict", "19", "--no-review"], env)
        self.assertIn("19／19", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", r.stdout)


if __name__ == "__main__":
    unittest.main()
