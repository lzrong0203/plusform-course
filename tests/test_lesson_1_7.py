"""1-7〈讀懂錯誤訊息：Traceback 從最下面看〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

重點：
  - p1～p8 每支藏一個錯（SyntaxError ×2、IndentationError、NameError、TypeError、ValueError ×2、ZeroDivisionError）：
    起點跑起來一定當掉、錯誤訊息的種類對；正確版印出註解寫的東西。
  - 計時題（check.py 的新指令 timer，只對 lesson.json timed 裡 from＝timer 的題目生效）：
    start 1-7 不複製 shop.py；timer 1-7 才複製、記下開始時間（第二次打不重算）；
    check 全對時，照「開始計時 → shop.py 最後一次存檔」印出花了幾分鐘，只記錄、不扣分；沒打 timer 就說這次沒計時。
  - 0-C 的 timed（照資料夾時間算）不受影響（test_regressions／test_flow 本來就測）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import json
import os
import shutil
import unittest
from datetime import datetime
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l17"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-7"
D = COURSE / "lessons" / LID
ERRS = {"p1": "SyntaxError", "p2": "SyntaxError", "p3": "IndentationError", "p4": "NameError",
        "p5": "TypeError", "p6": "ValueError", "p7": "ZeroDivisionError", "p8": "ValueError"}
MATCH = ["C", "F", "A", "E", "D", "B"]
AI = ["A", "B", "B"]


def start() -> Path:
    dest = L / "lessons" / LID
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(D / "start", dest)
    return dest


def ev(ids: list[str], ledger: Path | None = L) -> grader.Outcome:
    les = grader.load_lesson(LID, COURSE)
    return grader.evaluate(les, ledger, only=[c for c in les.checks if c["id"] in ids])


def answer(name: str, answers: list[str]) -> None:
    p = L / "lessons" / LID / name
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def progress() -> dict:
    return json.loads((L / ".check" / "progress.json").read_text(encoding="utf-8"))


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Programs(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_programs_crash_with_the_right_error(self):
        out = ev(list(ERRS))
        for r in out.results:
            self.assertFalse(r.ok, r.id)
            self.assertIn(ERRS[r.id], r.detail, (r.id, r.detail))

    def test_syntax_errors_print_nothing_but_runtime_errors_print_first(self):
        env = grader.Env(L)
        p1 = env.run_file(L / "lessons" / LID / "p1.py")
        self.assertEqual(p1.stdout, "")   # SyntaxError：一行都不跑（早餐也沒印）
        self.assertNotIn("Traceback", p1.stderr)
        p4 = env.run_file(L / "lessons" / LID / "p4.py")
        self.assertEqual(p4.stdout.strip(), "午餐 120 晚餐 150")   # NameError：前面的行已經跑了
        self.assertIn("Did you mean: 'total'?", p4.stderr)
        p8 = env.run_file(L / "lessons" / LID / "p8.py")
        self.assertIn("line 5", p8.stderr)   # 錯誤出現在第 5 行，要改的是第 4 行
        self.assertIn("'午餐'", p8.stderr)

    def test_references_pass_every_program(self):
        work = L / "lessons" / LID
        for name in ERRS:
            shutil.copy(D / "reference" / f"{name}.py", work / f"{name}.py")
        out = ev(list(ERRS))
        self.assertEqual([r.ok for r in out.results], [True] * 8, [(r.id, r.detail) for r in out.results if not r.ok])

    def test_deleting_the_broken_line_is_not_a_fix(self):
        work = L / "lessons" / LID
        (work / "p1.py").write_text('# 印出今天三餐的花費\nprint("早餐", 65)\nprint("晚餐", 150)\n', encoding="utf-8")
        r = ev(["p1"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("印出來的跟應該的不一樣", r.detail)

    def test_other_fixes_print_the_same(self):
        work = L / "lessons" / LID
        (work / "p5.py").write_text('# 印出午餐，再印出今天一共花多少\nlunch = 120\nprint("午餐", lunch)\ntotal = 65 + lunch\nprint("今天花了", total, "元")\n', encoding="utf-8")
        self.assertTrue(ev(["p5"]).results[0].ok)


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_match_answers(self):
        answer("match.txt", MATCH)
        out = ev(["match"])
        self.assertEqual([r.ok for r in out.results], [True] * 6, [r.detail for r in out.results])
        answer("match.txt", ["c", "f. 除以 0", "A", "e", "d", "B"])
        self.assertEqual([r.ok for r in ev(["match"]).results], [True] * 6)
        answer("match.txt", ["A", "F", "A", "E", "D", "B"])
        first = ev(["match"]).results[0]
        self.assertFalse(first.ok)
        self.assertIn("NameError", first.detail)

    def test_ai_help_answers(self):
        answer("ai_help.txt", AI)
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [True] * 3, [r.detail for r in out.results])
        answer("ai_help.txt", ["C", "A", "A"])
        self.assertEqual([r.ok for r in ev(["ai"]).results], [False] * 3)


class Timer(unittest.TestCase):
    def setUp(self):
        self.home = fresh_dir("l17_home")
        self.t0 = "2026-11-15T20:00:00+08:00"
        self.env = make_env(self.home, now=self.t0)
        r = run_check(["setup", str(L)], self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for p in (L / "lessons" / LID, L / ".check"):
            if p.exists():
                shutil.rmtree(p)

    def test_start_does_not_copy_the_timed_program(self):
        r = run_check(["start", "1-07"], self.env)
        self.assertIn("uv run check.py timer 1-7", r.stdout)
        self.assertTrue((L / "lessons" / LID / "p8.py").is_file())
        self.assertFalse((L / "lessons" / LID / "shop.py").exists())
        res = ev(["shop"]).results[0]
        self.assertFalse(res.ok)
        self.assertIn("uv run check.py timer 1-7", res.detail)

    def test_timer_copies_and_keeps_the_first_start(self):
        r = run_check(["timer", "1-7"], self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-7/shop.py", r.stdout)
        self.assertIn("開始計時：20:00", r.stdout)
        self.assertIn("只記錄、不扣分", r.stdout)
        self.assertEqual(progress()["lessons"]["1-7"]["timers"]["shop"], self.t0)
        later = make_env(self.home, now="2026-11-15T20:30:00+08:00")
        r = run_check(["timer", "1-7"], later)
        self.assertIn("已經有了，沒有蓋掉", r.stdout)
        self.assertIn("這次不重新算", r.stdout)
        self.assertEqual(progress()["lessons"]["1-7"]["timers"]["shop"], self.t0)

    def test_timer_on_a_lesson_without_timed_questions(self):
        r = run_check(["timer", "1-6"], self.env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("沒有計時題", r.stdout)

    def test_start_shop_crashes_far_from_the_real_bug(self):
        run_check(["timer", "1-7"], self.env)
        res = ev(["shop"]).results[0]
        self.assertFalse(res.ok)
        self.assertIn("TypeError", res.detail)
        self.assertIn("unsupported operand type(s) for +: 'int' and 'str'", res.detail)

    def _fix_shop(self, minutes: float) -> None:
        shop = L / "lessons" / LID / "shop.py"
        shutil.copy(D / "reference" / "shop.py", shop)
        t = datetime.fromisoformat(self.t0).timestamp() + minutes * 60
        os.utime(shop, (t, t))

    def test_full_run_prints_minutes_from_timer_to_last_save(self):
        run_check(["start", "1-7"], self.env)
        run_check(["timer", "1-7"], self.env)
        work = L / "lessons" / LID
        for name in ERRS:
            shutil.copy(D / "reference" / f"{name}.py", work / f"{name}.py")
        answer("match.txt", MATCH)
        answer("ai_help.txt", AI)
        self._fix_shop(4.2)
        done = make_env(self.home, now="2026-11-15T20:50:00+08:00")
        r = run_check(["1-07", "--predict", "18", "--no-review"], done)
        self.assertIn("18／18", r.stdout, r.stdout + r.stderr)
        self.assertIn("計時題 shop.py：照檔案時間算，從開始計時到最後一次存檔，大約花了 4 分鐘（參考是 10 分鐘內）。做到了！", r.stdout)
        self.assertIn("只記錄、不扣分", r.stdout)
        self.assertEqual(progress()["lessons"]["1-7"]["timed"]["shop"], 4.2)
        r = run_check(["1-07", "--predict", "18", "--no-review"], done)
        self.assertNotIn("大約花了", r.stdout)   # 只在第一次通過時印

    def test_slow_run_is_only_noted(self):
        run_check(["timer", "1-7"], self.env)
        self._fix_shop(25)
        les = grader.load_lesson(LID, COURSE)
        r = run_check(["1-07", "--predict", "1", "--no-review"], make_env(self.home, now="2026-11-15T21:00:00+08:00"))
        self.assertIn("大約花了 25 分鐘（參考是 10 分鐘內）。這次先記下來，多練幾次就會變快。", r.stdout)
        self.assertEqual(les.meta["timed"]["shop"]["from"], "timer")

    def test_copied_by_hand_is_not_timed(self):
        (L / "lessons" / LID).mkdir(parents=True, exist_ok=True)
        shutil.copy(D / "reference" / "shop.py", L / "lessons" / LID / "shop.py")
        r = run_check(["1-07", "--predict", "1", "--no-review"], self.env)
        self.assertIn("沒有先打 uv run check.py timer 1-7，這次沒有計時（不影響過關）", r.stdout)
        self.assertNotIn("shop", progress()["lessons"]["1-7"].get("timed", {}))


if __name__ == "__main__":
    unittest.main()
