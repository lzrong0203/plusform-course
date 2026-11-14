"""1-8〈比較、邏輯與 assert〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

第③圈從這課起改寫 assert：學員的 checks_budget.py 交給 chaff 的 assert 模式（1-9 也用同一個模式），
check 把它拿去跑正確版和 3 個壞版本（runner.py 的 asserts：每個版本各開一個子程序、有逾時，學員印的字不混進結果），
正確版上要全部成立、每個壞版本至少一條不成立。這課在 checks.json 加了兩個旗標（只對寫了它的 checks.json 生效）：
  bool_hints：True／False 寫成小寫或加了引號時給白話提示；只寫 assert over_budget(...)、assert not over_budget(...) 也報出交回的值
  no_marks：特殊作答（# 已知會當掉、# 需求有問題）1-9 才教，這課行尾的註解一律當成一般的檢查
三個壞版本：m1 大於寫成大於等於（剛好花到預算才抓得到，這課的主角）、m2 兩個數字比反了、m3 自己多給 100 元的緩衝（只超過一點點才抓得到）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import copy
import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l18"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-8"
D = COURSE / "lessons" / LID
HEAD = "from budget import over_budget\n\n"
# 影片裡熊的五條：多的、少的、多很多、零元、只多 50 元，就是沒有「剛好花到預算」
BEAR = ["assert over_budget(1200, 1000) == True", "assert over_budget(800, 1000) == False",
        "assert over_budget(3500, 3000) == True", "assert over_budget(0, 3000) == False",
        "assert over_budget(1050, 1000) == True"]


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


def r3(lines: list[str], head: str = HEAD, tweak=None) -> grader.Outcome:
    write(L / "lessons" / LID / "checks_budget.py", head + "\n".join(lines) + "\n")
    return ev(["r3"], tweak=tweak)


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

    def test_teacher_asserts_catch_all_three(self):
        teacher = (D / "answers" / "checks_budget.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "checks_budget.py", teacher)
        out = ev(["r3"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 6 行抓到")   # 剛好花到預算：over_budget(1000, 1000) == False
        self.assertEqual(part(out, "m2").note, "被第 4 行抓到")   # 比反了：第一條就抓到
        self.assertEqual(part(out, "m3").note, "被第 7 行抓到")   # 只多 1 元
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_bear_five_let_the_boundary_slip(self):
        out = r3(BEAR)
        self.assertTrue(part(out, "count").ok)
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
        self.assertFalse(part(out, "m1").ok)
        self.assertIn("剛好花到預算", part(out, "m1").detail)
        self.assertTrue(part(out, "m2").ok)
        self.assertTrue(part(out, "m3").ok)
        self.assertEqual(part(out, "m3").note, "被第 7 行抓到")   # 只多 50 元的那一條
        self.assertIn("你的檢查抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)
        # 每行壓在 68 欄內（VHS 錄影 70 欄）
        for line in out.summaries:
            self.assertLessEqual(sum(2 if ord(ch) > 0x2E7F else 1 for ch in line), 68, line)

    def test_adding_the_equal_case_catches_m1(self):
        out = r3(BEAR + ["assert over_budget(1000, 1000) == False"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 8 行抓到")

    def test_start_file_is_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你寫了 1 條檢查，這課要至少 5 條", part(out, "count").detail)
        self.assertTrue(part(out, "wheat").ok)   # 起點檔的範例在正確版上成立
        self.assertFalse(part(out, "m1").ok)
        self.assertIn("先寫滿 5 條檢查", part(out, "m1").detail)   # 寫滿以前不講溜過去的是哪一種

    def test_equal_case_written_as_true_is_wrong_on_reference(self):
        out = r3(BEAR[:4] + ["assert over_budget(1000, 1000) == True"])
        self.assertFalse(part(out, "wheat").ok)
        d = part(out, "wheat").detail
        self.assertIn("第 7 行", d)
        self.assertIn("正確版算出來是False", d)
        self.assertIn("再對一次需求卡", d)
        self.assertNotIn("需求有問題", d)   # no_marks：這課還沒教特殊作答

    def test_single_equal_sign_is_explained(self):
        out = r3(BEAR[:4] + ["assert over_budget(1000, 1000) = False"])
        d = part(out, "count").detail
        self.assertIn("語法錯誤", d)
        self.assertIn("兩個等號 ==", d)

    def test_lowercase_true_gets_a_plain_hint(self):
        out = r3(BEAR[:4] + ["assert over_budget(1001, 1000) == true"])
        d = part(out, "wheat").detail
        self.assertIn("第一個字母要大寫", d)
        self.assertNotIn("已知會當掉", d)

    def test_quoted_true_is_text(self):
        out = r3(BEAR[:4] + ['assert over_budget(1001, 1000) == "True"'])
        d = part(out, "wheat").detail
        self.assertIn("不加引號", d)
        self.assertIn("\"True\" 是文字", d)

    def test_bare_and_not_forms_work_and_report_the_value(self):
        good = ["assert over_budget(1200, 1000)", "assert not over_budget(800, 1000)", "assert not over_budget(1000, 1000)",
                "assert over_budget(1001, 1000)", "assert not over_budget(0, 1000)"]
        out = r3(good)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        out = r3(good[:4] + ["assert over_budget(1000, 1000)"])
        d = part(out, "wheat").detail
        self.assertIn("over_budget(1000, 1000) 在正確版交回 False", d)
        out = r3(good[:4] + ["assert not over_budget(1200, 1000)"])
        self.assertIn("over_budget(1200, 1000) 在正確版交回 True", part(out, "wheat").detail)

    def test_marks_are_plain_checks_in_this_lesson(self):
        out = r3(BEAR + ["assert over_budget(1000, 1000) == False  # 已知會當掉"])
        self.assertFalse(any(getattr(r, "special", False) for r in out.results))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_missing_import_line(self):
        out = r3(BEAR, head="")
        d = part(out, "wheat").detail
        self.assertIn("from budget import", d)

    def test_assert_inside_if_is_not_counted(self):
        out = r3(BEAR[:4] + ["if True:", "    assert over_budget(1000, 1000) == False"])
        self.assertFalse(part(out, "count").ok)
        self.assertTrue(any("寫在 for、if 或 def 裡面" in s for s in out.summaries))

    def test_a_hanging_line_is_stopped_and_each_version_runs_alone(self):
        """學員的檔會被執行：卡住的那一行被逾時收掉，其他版本照樣跑（每個版本各一個子程序）。"""
        # 正確版的 over_budget(1, 0) 是 True：迴圈停不下來；壞版本 2（比反了）是 False，照常往下跑
        lines = ["x = 0", "while over_budget(1, 0):", "    x = x + 1"] + BEAR + ["assert over_budget(1000, 1000) == False"]
        write(L / "lessons" / LID / "checks_budget.py", HEAD + "\n".join(lines) + "\n")
        les = grader.load_lesson(LID, COURSE)
        spec = dict(next(c for c in les.checks if c["id"] == "r3"), timeout=2)
        _ctx, checkers = grader.build(les, L, only=[spec])
        ch = checkers[0]
        parsed = ch.parse()
        st, _ = ch.statuses(parsed.checks, parsed.marks)
        self.assertTrue(all(row.get("stuck") for row in st["reference"]), st["reference"])
        self.assertIn("卡在無窮迴圈", st["reference"][0]["error"])
        self.assertEqual([row["status"] for row in st["m2"]], ["fail", "fail", "fail", "fail", "fail", "pass"])
        out = r3(lines, tweak=lambda c: c.update(timeout=2))
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("無窮迴圈", part(out, "wheat").detail)

    def test_printing_in_the_checks_does_not_leak_into_results(self):
        out = r3(['print("我先印一行")'] + BEAR + ["assert over_budget(1000, 1000) == False"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class OtherChecks(unittest.TestCase):
    def setUp(self):
        start()

    def test_reference_programs_pass_and_start_does_not(self):
        work = L / "lessons" / LID
        ids = ["over1", "over2", "wk1", "wk2", "wk3"]
        self.assertFalse(any(r.ok for r in ev(ids).results))
        shutil.copy(D / "reference" / "over.py", work / "over.py")
        shutil.copy(D / "reference" / "weekend.py", work / "weekend.py")
        out = ev(ids)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_greater_equal_fails_the_exact_budget(self):
        work = L / "lessons" / LID
        src = (D / "reference" / "over.py").read_text(encoding="utf-8").replace("spent > budget", "spent >= budget")
        write(work / "over.py", src)
        out = ev(["over1", "over2"])
        self.assertTrue(part(out, "over1").ok)
        self.assertFalse(part(out, "over2").ok)
        self.assertIn("大於 >，不是大於等於 >=", part(out, "over2").detail)

    def test_or_with_a_bare_string_is_caught(self):
        work = L / "lessons" / LID
        src = (D / "reference" / "weekend.py").read_text(encoding="utf-8").replace('day == "六" or day == "日"', 'day == "六" or "日"')
        write(work / "weekend.py", src)
        out = ev(["wk1", "wk2", "wk3"])
        self.assertTrue(part(out, "wk1").ok)
        self.assertFalse(part(out, "wk3").ok)
        self.assertIn("有字的字串", part(out, "wk3").detail)

    def test_truth_answers(self):
        answer("truth.txt", ["False", "true", "FALSE", " False "])
        out = ev(["truth"])
        self.assertEqual([r.ok for r in out.results], [True] * 4, [r.detail for r in out.results])
        answer("truth.txt", ["True", "False", "True", "True"])
        self.assertEqual([r.ok for r in ev(["truth"]).results], [False] * 4)

    def test_ai_check_answers(self):
        answer("ai_check.txt", ["A", "c", "B"])
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [True] * 3, [r.detail for r in out.results])

    def test_full_run_through_check_py(self):
        """check.py 1-08（課號補 0 也認得）：全對 17 題。"""
        home = fresh_dir("l18_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_check(["start", "1-08"], env, stdin="")
        self.assertIn("uv run check.py 1-8", r.stdout)
        work = L / "lessons" / LID
        self.assertTrue((work / "budget.py").is_file())
        shutil.copy(D / "reference" / "over.py", work / "over.py")
        shutil.copy(D / "reference" / "weekend.py", work / "weekend.py")
        shutil.copy(D / "answers" / "checks_budget.py", work / "checks_budget.py")
        answer("truth.txt", ["False", "True", "False", "False"])
        answer("ai_check.txt", ["A", "C", "B"])
        r = run_check(["1-08", "--predict", "17", "--no-review"], env)
        self.assertIn("17／17", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", r.stdout)


if __name__ == "__main__":
    unittest.main()
