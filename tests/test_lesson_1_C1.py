"""1-C1〈檢核站 1〉：交卷、訂正、矯正包、卷 B 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

檢核站跟一般課不一樣的地方（check.py 的 cmd_checkpoint、start_checkpoint，只對 lesson.json 寫了 checkpoint 的課生效）：
  - 第一次 check 是交卷，成績只照這次算（10 題過 8 題以上算過）；之後再打是訂正，不改成績。還有題目空著不算交卷（--submit 例外）。
  - start 先問預測分數、交卷再問一次，兩次和實際都記進校準曲線；20 分鐘照作答檔的存檔時間記下來，只記錄、不擋。
  - 沒過把矯正包寫進帳本（錯的題目 → 原課章節時間碼＋練習檔）；卷 B 放在 lessons/1-C1/B/，卷 A 交卷的隔天以後才能 start。
grader 的兩個新東西：run 的 swap（把 total = 1730 換成 2026 再跑一次）、當掉時記下錯誤種類；answers 的題目可以有自己的 choices。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l1c1"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
D = COURSE / "lessons" / "1-C1"
DAY1, DAY1_LATE, DAY2 = "2026-11-16T19:00:00+08:00", "2026-11-16T23:30:00+08:00", "2026-11-17T20:00:00+08:00"
RIGHT_A = ["11/15", "4", "50", "465 50", "196 2", "B"]
RIGHT_B = ["2026-11", "3", "50", "275 50", "102 2", "A"]
WRITE_A = (D / "reference" / "write.py").read_text(encoding="utf-8")
FIX_A = (D / "reference" / "fix.py").read_text(encoding="utf-8")


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def answer(lid: str, answers: list[str]) -> None:
    p = L / "lessons" / lid / "trace.txt"
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def fresh_start(lid: str = "1-C1") -> Path:
    dest = L / "lessons" / lid
    if dest.exists():
        shutil.rmtree(dest)
    src = D / ("B/start" if lid.endswith("B") else "start")
    shutil.copytree(src, dest)
    return dest


def ev(lid: str, ids: list[str] | None = None) -> grader.Outcome:
    les = grader.load_lesson(lid, COURSE)
    return grader.evaluate(les, L, only=None if ids is None else [c for c in les.checks if c["id"] in ids])


def part(out: grader.Outcome, rid: str) -> grader.Result:
    return next(r for r in out.results if r.id == rid)


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Grading(unittest.TestCase):
    """grader：卷 A、卷 B 的正確版全過；swap、錯誤種類、題目自己的選項。"""

    def setUp(self):
        fresh_start("1-C1")

    def test_ids_and_paper_b_folder(self):
        info = grader.course_info(COURSE)
        for raw, want in (("1-C1", "1-C1"), ("1-c1", "1-C1"), ("1-C1B", "1-C1B"), ("1-c1b", "1-C1B"), ("1-C1-B", "1-C1B"), ("１－Ｃ１", "1-C1")):
            self.assertEqual(grader.normalize_id(raw, info), want, raw)
        b = grader.load_lesson("1-C1B", COURSE)
        self.assertEqual(b.dir, D / "B")
        self.assertEqual(b.meta["paper_of"], "1-C1")
        self.assertNotIn("1-C1B", grader.available_lessons(COURSE))   # 卷 B 不在課表裡
        self.assertIn("1-C1", grader.available_lessons(COURSE))

    def test_reference_answers_pass_all_ten(self):
        answer("1-C1", RIGHT_A)
        write(L / "lessons/1-C1/fix.py", FIX_A)
        write(L / "lessons/1-C1/write.py", WRITE_A)
        out = ev("1-C1")
        self.assertEqual(out.total, 10)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual([r.stage for r in out.results].count("第一部分 追蹤"), 6)

    def test_paper_b_reference_passes_and_start_does_not(self):
        fresh_start("1-C1B")
        out = ev("1-C1B")
        self.assertFalse(any(r.ok for r in out.results[6:]))
        answer("1-C1B", RIGHT_B)
        write(L / "lessons/1-C1B/fix.py", (D / "B/reference/fix.py").read_text(encoding="utf-8"))
        write(L / "lessons/1-C1B/write.py", (D / "B/reference/write.py").read_text(encoding="utf-8"))
        out = ev("1-C1B")
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_question_level_choices_and_spacing(self):
        answer("1-C1", ["11 / 15", "4行", "50 元", "465, 50", "196、2", "<class 'float'>"])
        out = ev("1-C1", ["trace"])
        self.assertEqual([r.ok for r in out.results], [True] * 6, [r.detail for r in out.results])
        answer("1-C1", ["11 15", "5", "35", "415 50", "163 1", "A"])
        out = ev("1-C1", ["trace"])
        self.assertEqual([r.ok for r in out.results], [False] * 6)
        answer("1-C1", ["11/15", "4", "50", "465 50", "196 2", "float"])
        r = part(ev("1-C1", ["trace"]), "trace-t6")
        self.assertFalse(r.ok)
        self.assertIn("只要寫一個字母（A、B 或 C）", r.detail)

    def test_swap_catches_hardcoded_answer(self):
        write(L / "lessons/1-C1/write.py", 'total = 1730\nprint("每天", 247, "元")\nprint("剩下", total % 7, "元")\nprint("驗算", 247 * 7 + total % 7)\n')
        out = ev("1-C1", ["write-out", "write-swap"])
        self.assertTrue(part(out, "write-out").ok)
        r = part(out, "write-swap")
        self.assertFalse(r.ok)
        self.assertIn("check 把你的 total = 1730 換成 total = 2026", r.detail)
        self.assertIn("每天 289 元", r.detail)
        self.assertIn("每天 247 元", r.detail)

    def test_swap_needs_the_total_line_and_accepts_spacing_and_comment(self):
        write(L / "lessons/1-C1/write.py", WRITE_A.replace("total = 1730", "money = 1730").replace("total", "money"))
        out = ev("1-C1", ["write-out", "write-swap"])
        self.assertTrue(part(out, "write-out").ok)
        self.assertIn("找不到 total = 1730 這一行", part(out, "write-swap").detail)
        write(L / "lessons/1-C1/write.py", WRITE_A.replace("total = 1730", "total=1730  # 這週的零用錢"))
        out = ev("1-C1", ["write-out", "write-swap"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_fix_records_the_error_kind(self):
        out = ev("1-C1", ["fix-run", "fix-out"])   # 起點：少一個引號
        self.assertEqual(part(out, "fix-run").data.get("error"), "SyntaxError")
        self.assertFalse(part(out, "fix-out").ok)
        write(L / "lessons/1-C1/fix.py", (D / "start/fix.py").read_text(encoding="utf-8").replace('"元)', '"元")'))
        out = ev("1-C1", ["fix-run"])
        self.assertEqual(part(out, "fix-run").data.get("error"), "TypeError")
        write(L / "lessons/1-C1/fix.py", FIX_A.replace("total // 3", "total / 3"))
        out = ev("1-C1", ["fix-run", "fix-out"])
        self.assertTrue(part(out, "fix-run").ok)
        self.assertIn("53.333333333333336", part(out, "fix-out").detail)
        write(L / "lessons/1-C1/fix.py", 'print("一共 平均")\n')   # 兩個詞擠在同一行：不算「印出兩行」（Codex 審卷 B 時抓到判分比說明寬）
        self.assertFalse(part(ev("1-C1", ["fix-run"]), "fix-run").ok)
        write(L / "lessons/1-C1/fix.py", 'print("一共  160  元")\nprint()\nprint("平均",  53, "元")\n')   # 多打的空格、空白的行不算錯（照 README 的說法）
        out = ev("1-C1", ["fix-run", "fix-out"])
        self.assertTrue(part(out, "fix-run").ok and part(out, "fix-out").ok, [r.detail for r in out.results])


class Flow(unittest.TestCase):
    """check.py：start、交卷、訂正、矯正包、卷 B、status。"""

    @classmethod
    def setUpClass(cls):
        cls.home = fresh_dir("l1c1_home")
        cls.env = lambda self, now: make_env(self.home, now=now)

    def setUp(self):
        for lid in ("1-C1", "1-C1B"):
            d = L / "lessons" / lid
            if d.exists():
                shutil.rmtree(d)
        if (L / ".check").exists():
            shutil.rmtree(L / ".check")
        r = run_check(["setup", str(L)], make_env(self.home))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def run_(self, args, now):
        return run_check(args, make_env(self.home, now=now))

    def rabbit_paper_a(self):
        """果凍兔：追蹤第 2 題錯（以為註解那一行也印）、fix.py 平均用了 /、write.py 每天的錢寫死 247 → 7／10。"""
        work = L / "lessons/1-C1"
        answer("1-C1", ["11/15", "5", "50", "465 50", "196 2", "B"])
        write(work / "fix.py", FIX_A.replace("total // 3", "total / 3"))
        write(work / "write.py", 'total = 1730\nprint("每天", 247, "元")\nprint("剩下", total % 7, "元")\nprint("驗算", 247 * 7 + total % 7)\n')

    def test_start_asks_prediction_and_unfinished_is_not_a_submission(self):
        before = snapshot(COURSE)
        r = self.run_(["start", "1-C1", "--predict", "8"], DAY1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-C1/trace.txt", r.stdout)
        self.assertIn("記下來了：開始前你猜會過 8／10 題。交卷時會再問一次。", r.stdout)
        self.assertIn("uv run check.py 1-C1（交卷）", r.stdout)
        r = self.run_(["1-C1", "--predict", "9"], DAY1)
        self.assertEqual(r.returncode, 1)
        self.assertIn("這次先不算交卷", r.stdout)
        self.assertIn("trace.txt 第 1、2、3、4、5、6 題還沒寫", r.stdout)
        self.assertIn("fix.py 還沒改", r.stdout)
        self.assertIn("write.py 還沒寫程式", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertNotIn("submitted", prog["lessons"]["1-C1"])
        self.assertEqual(snapshot(COURSE), before)

    def test_fail_writes_the_remedial_pack_and_redo_does_not_change_the_score(self):
        self.run_(["start", "1-C1", "--predict", "8"], DAY1)
        self.rabbit_paper_a()
        r = self.run_(["1-C1", "--predict", "9", "--no-review"], "2026-11-16T19:20:00+08:00")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("結果：過了 7／10 題（8 題以上算過）", out)
        self.assertIn("✗ 第一部分 追蹤  5／6", out)
        self.assertIn("你猜 9 題，實際過了 7 題：高估了 2 題", out)
        self.assertIn("（開始前你猜 8 題，做完猜 9 題，實際 7 題。）", out)
        self.assertIn("這次沒過。矯正包在帳本的 lessons/1-C1/矯正包.md：", out)
        self.assertIn("  追蹤第 2 題 → 1-1 影片 1:46 起", out)
        self.assertIn("  修好：印出來的不一樣 → 1-4 影片 1:45 起", out)
        self.assertIn("  手寫：金額換了就不對 → 1-4 影片 3:51 起", out)
        self.assertIn("練完，明天以後考卷 B：uv run check.py start 1-C1B", out)
        for line in out.splitlines():   # 影片錄的是這一段：70 欄寫得完（中文算兩欄）
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        pack = (L / "lessons/1-C1/矯正包.md").read_text(encoding="utf-8")
        self.assertIn("正確答案：4", pack)
        self.assertIn("1-4〈數字與運算：分帳的零頭〉3:51 起", pack)
        self.assertIn("11/17 起", pack)
        self.assertEqual(sorted(p.name for p in (L / "lessons/1-C1/practice").iterdir()), ["p_math.py", "p_print.py", "p_write.py"])
        r = self.run_(["1-C1", "--no-review"], "2026-11-16T19:40:00+08:00")
        self.assertIn("（這是訂正：成績照 11/16 第一次交卷算，過了 7／10 題。）", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-C1"]["submitted"]["passed"], 7)
        self.assertNotIn("first_pass", prog["lessons"]["1-C1"])
        rows = [json.loads(x) for x in (L / ".check/attempts.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([a["predicted"] for a in rows], [9, None])   # 訂正不問預測、不進校準曲線

    def test_paper_b_waits_for_the_next_day_and_passing_b_passes_the_checkpoint(self):
        r = self.run_(["start", "1-C1B"], DAY1)
        self.assertIn("要等卷 A 交卷以後才能考", r.stdout)
        self.run_(["start", "1-C1", "--predict", "8"], DAY1)
        self.rabbit_paper_a()
        self.run_(["1-C1", "--predict", "9", "--no-review"], "2026-11-16T19:20:00+08:00")
        r = self.run_(["start", "1-C1B", "--predict", "9"], DAY1_LATE)
        self.assertEqual(r.returncode, 1)
        self.assertIn("卷 B 要隔天以後才能考（你在 11/16 交了卷 A）", r.stdout)
        self.assertFalse((L / "lessons/1-C1B").exists())
        r = self.run_(["start", "1-c1b", "--predict", "9"], DAY2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-C1B/write.py", r.stdout)
        answer("1-C1B", RIGHT_B)
        write(L / "lessons/1-C1B/fix.py", (D / "B/reference/fix.py").read_text(encoding="utf-8"))
        write(L / "lessons/1-C1B/write.py", (D / "B/reference/write.py").read_text(encoding="utf-8").replace("each = total // 6", "each = 391"))
        r = self.run_(["1-C1B", "--predict", "9", "--no-review"], "2026-11-17T20:18:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 9／10 題（8 題以上算過）", r.stdout)
        self.assertIn("✓ 過了！檢核站 1 通過。", r.stdout)
        self.assertIn("錯的那 1 題，矯正包一樣寫好了：帳本的 lessons/1-C1B/矯正包.md", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-C1"]["passed_via"], "B")
        r = self.run_(["status"], "2026-11-17T20:20:00+08:00")
        self.assertIn("✓ 1-C1 檢核站 1　11/17 通過；卷 A 11/16 交卷 7／10（沒過）；卷 B 11/17 交卷 9／10", r.stdout)
        self.assertIn("1C1B ", r.stdout)   # 校準曲線：卷 B 寫成 1C1B，條子才對得齊
        self.assertIn("1-C1 交卷：開始前猜 8、做完猜 9、實際 7／10", r.stdout)

    def test_pass_on_paper_a_and_submit_flag(self):
        self.run_(["start", "1-C1", "--predict", "10"], DAY1)
        answer("1-C1", RIGHT_A[:5] + [""])
        write(L / "lessons/1-C1/fix.py", FIX_A)
        write(L / "lessons/1-C1/write.py", WRITE_A)
        r = self.run_(["1-C1", "--predict", "10", "--no-review"], "2026-11-16T19:15:00+08:00")
        self.assertIn("trace.txt 第 6 題還沒寫", r.stdout)
        r = self.run_(["1-C1", "--predict", "10", "--submit", "--no-review"], "2026-11-16T19:15:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 9／10 題", r.stdout)
        self.assertIn("✓ 過了！檢核站 1 通過。", r.stdout)
        r = self.run_(["start", "1-C1B"], DAY2)
        self.assertIn("就過了檢核站 1，卷 B 不用考", r.stdout)


if __name__ == "__main__":
    unittest.main()
