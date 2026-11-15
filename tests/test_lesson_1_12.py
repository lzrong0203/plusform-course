"""1-12〈Lv1 上關卡：帳本 v0.1〉：考卷（交卷、訂正、矯正包、卷 B）、第二部分（自評的表單寫了沒）、第三部分（分帳的 assert）、升級的回歸測試。

1-12 是第一個「有考卷的關卡」（check.py 的 cmd_exam_gate，只對 lesson.json 寫了 gate_parts 的關卡生效）：
  - 第一部分是考卷，跟檢核站一樣：20 題（讀程式 14、從零寫 6）、第一次交卷過 16 題以上算過；之後再打是訂正，不改成績；
    沒過領矯正包（終端機只列前 3 題，其他寫在矯正包裡），卷 A 交卷的隔天以後考卷 B（lessons/1-12/B/）。
  - 第二、三部分的起點檔在 start_later/，第一次交卷以後才放進帳本；之後每次打 1-12（或 1-12B）都會檢查，哪一次全過就記下日期。
  - 第二部分是自評：tutor.md 的三個「家教問：」「我的回答：」都寫了就算交了（grader 的 filled，1-12 加）。
  - 第三部分替 share() 寫 assert（chaff 的 assert 模式），三個壞版本都要抓到。
  - 第一部分過了（卷 A 或卷 B）、第二部分交了、第三部分全過，練習天數滿 7 天才升級（practice_days，跟 0-C 一樣）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l112"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
D = COURSE / "lessons" / "1-12"
DAY1, DAY1_LATE, DAY2 = "2026-11-20T18:00:00+08:00", "2026-11-20T23:30:00+08:00", "2026-11-21T19:00:00+08:00"
RIGHT_A = ["9", "3", "3", "6", "C", "A", "TypeError", "6", "A"]
RIGHT_B = ["12", "4", "2", "8", "A", "B", "TypeError", "7", "C"]
RABBIT_A = ["9", "5", "3", "6", "C", "A", "TypeError", "6", "B"]   # 第 2 題以為 continue 不會跳過、第 9 題以為改 input 那一行就好


def text(rel: str) -> str:
    return (D / rel).read_text(encoding="utf-8")


def write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.encode("utf-8"))
    return path


def answer(lid: str, answers: list[str]) -> None:
    p = L / "lessons" / lid / "trace.txt"
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def touch_at(lid: str, when: str) -> None:
    """作答檔的存檔時間（check 照「開始到最後一次存檔」記時間）。"""
    t = datetime.fromisoformat(when).timestamp()
    for f in ("trace.txt", "parsons.py", "fix.py", "ledger.py"):
        os.utime(L / "lessons" / lid / f, (t, t))


def fresh_start(lid: str = "1-12", later: bool = False) -> Path:
    dest = L / "lessons" / lid
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(D / ("B/start" if lid.endswith("B") else "start"), dest)
    if later:
        shutil.copytree(D / "start_later", dest, dirs_exist_ok=True)
    return dest


def ev(lid: str, ids: list[str] | None = None) -> grader.Outcome:
    les = grader.load_lesson(lid, COURSE)
    return grader.evaluate(les, L, only=None if ids is None else [c for c in les.checks if c["id"] in ids])


def part(out: grader.Outcome, rid: str) -> grader.Result:
    return next(r for r in out.results if r.id == rid)


COUNT_AFTER_Q = ('    if text == "q":\n        break\n    if text == "":\n        continue\n    count = count + 1\n',
                 '    if text == "q":\n        break\n    count = count + 1\n    if text == "":\n        continue\n')


def rabbit_fix(src: str) -> str:
    """果凍兔的 fix.py：兩個錯誤訊息都修好、q 不算一筆了，可是 count 加 1 還在 continue 上面（空白的一行也算一筆）。"""
    return src.replace(*COUNT_AFTER_Q)


def rabbit_ledger(src: str) -> str:
    """果凍兔的 ledger.py：黃燈寫成 ratio < 1（剛好 100% 變紅燈）、每人用 /（有小數點）。"""
    return src.replace("elif ratio <= 1:", "elif ratio < 1:").replace("total // people", "total / people")


TUTOR_QA = [("如果一開始就打 q，你的程式會印出什麼？", "小計和合計都是 0 元，燈號是綠燈，因為迴圈一次都沒做。"),
            ("剛好花完預算，會亮哪一個燈？", "黃燈，因為我寫 ratio <= 1，剛好等於也成立。"),
            ("分帳為什麼用 // 不用 /？", "// 除完只留整數，零頭另外用 % 算，加起來才會等於合計。")]


def fill_tutor(path: Path, n: int = 3) -> None:
    t = path.read_text(encoding="utf-8")
    for q, a in TUTOR_QA[:n]:
        t = t.replace("家教問：\n\n我的回答：", f"家教問：{q}\n\n我的回答：{a}", 1)
    path.write_text(t, encoding="utf-8")


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Grading(unittest.TestCase):
    """grader：卷 A、卷 B 的正確版全過；起點檔、常見的錯、第二部分的表單、第三部分的壞版本。"""

    def setUp(self):
        fresh_start("1-12", later=True)

    def test_ids_and_paper_b_folder(self):
        info = grader.course_info(COURSE)
        for raw, want in (("1-12", "1-12"), ("1-12B", "1-12B"), ("1-12b", "1-12B"), ("1-12-B", "1-12B"), ("1-012b", "1-12B"),
                          ("1-C2B", "1-C2B"), ("1-c1b", "1-C1B")):
            self.assertEqual(grader.normalize_id(raw, info), want, raw)
        b = grader.load_lesson("1-12B", COURSE)
        self.assertEqual(b.dir, D / "B")
        self.assertEqual(b.meta["paper_of"], "1-12")
        self.assertEqual(grader.load_lesson("1-C2B", COURSE).dir, COURSE / "lessons/1-C2/B")
        self.assertNotIn("1-12B", grader.available_lessons(COURSE))
        self.assertIn("1-12", grader.available_lessons(COURSE))

    def test_reference_answers_pass_the_whole_exam(self):
        answer("1-12", RIGHT_A)
        for f in ("parsons.py", "fix.py", "ledger.py"):
            write(L / "lessons/1-12" / f, text(f"reference/{f}"))
        les = grader.load_lesson("1-12", COURSE)
        exam = [c for c in les.checks if not c.get("gate_part")]
        out = grader.evaluate(les, L, only=exam)
        self.assertEqual(out.total, 20)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results if not r.ok])
        stages = [r.stage for r in out.results]
        self.assertEqual((stages.count("讀程式"), stages.count("從零寫 v0.1")), (14, 6))   # 70／30

    def test_paper_b_reference_passes_and_start_does_not(self):
        fresh_start("1-12B")
        out = ev("1-12B")
        self.assertEqual(out.total, 20)
        self.assertFalse(any(r.ok for r in out.results if r.id.startswith(("pz", "fix", "ledger"))))
        answer("1-12B", RIGHT_B)
        for f in ("parsons.py", "fix.py", "ledger.py"):
            write(L / "lessons/1-12B" / f, text(f"B/reference/{f}"))
        out = ev("1-12B")
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results if not r.ok])
        a_ids = [r.id for r in grader.plan(grader.load_lesson("1-12", COURSE), L) if not r.id.startswith(("tutor", "r3"))]
        self.assertEqual([r.id for r in out.results], a_ids)   # 題目 id 跟卷 A 一樣（矯正包對照表共用）

    def test_trace_spacing_choices_and_common_mistakes(self):
        answer("1-12", ["9", "3 次", "3行", "6", "c. 什麼都不印", "A", "typeerror", "line 6", "a"])
        out = ev("1-12", ["trace"])
        self.assertEqual([r.ok for r in out.results], [True] * 9, [r.detail for r in out.results])
        # 常見的錯：continue 沒跳過（15、5）、print 當成在內層（6）、count 每天重來（2）、以為印綠燈、以為 / 有小數、錯誤種類寫成 ValueError、行號寫 3、改 input
        answer("1-12", ["15", "5", "6", "2", "B", "B", "ValueError", "3", "B"])
        out = ev("1-12", ["trace"])
        self.assertEqual([r.ok for r in out.results], [False] * 9)
        r = part(out, "trace-t9")
        self.assertIn("提示：B 的話，打 q 的時候", r.detail)

    def test_numbers_keep_spaces_and_one_choice_only(self):
        # Codex 審卷 B：「1 2」跟「12」是不一樣的輸出（keep_spaces）；「B 或 C」不算選了 B（strict_choice）
        fresh_start("1-12B")
        answer("1-12B", ["1 2", "4", "2", "8", "A 或 B", "B、C", "TypeError", "7", "C. 把第 7 行改成 count = count + int(text)"])
        out = ev("1-12B", ["trace"])
        self.assertEqual([r.ok for r in out.results], [False, True, True, True, False, False, True, True, True], [r.detail for r in out.results])
        self.assertIn("這題只能選一個", part(out, "trace-t5").detail)
        answer("1-12B", RIGHT_B[:5] + ["(B)", "TypeError", "第 7 行", "c"])
        out = ev("1-12B", ["trace"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_parsons_break_outside_loop_is_not_in_order(self):
        # Codex 審卷 B：print 放進 if、break 排到最外面，行數、縮排都對，ast 讀得懂，可是 compile 會說 'break' outside loop
        bad = "bank = 0\nweek = 0\nwhile True:\n    week = week + 1\n    bank = bank + 150\n    if bank >= 500:\n        print(\"第\", week, \"週存到\", bank, \"元\")\nbreak\n"
        write(L / "lessons/1-12/parsons.py", bad)
        out = ev("1-12", ["pz"])
        self.assertEqual([r.ok for r in out.results], [False, False])
        self.assertIn("不在迴圈裡", out.results[0].detail)
        write(L / "lessons/1-12/parsons.py", text("reference/parsons.py").replace(
            '        break\nprint("第", week, "週存到", bank, "元")\n', '        print("第", week, "週存到", bank, "元")\n        break\n'))
        out = ev("1-12", ["pz"])
        self.assertEqual([r.ok for r in out.results], [True, True], [r.detail for r in out.results])   # 印在 break 前面也對（排法不只一種）

    def test_fix_meets_two_error_messages_then_the_two_counting_mistakes(self):
        start = text("start/fix.py")
        out = ev("1-12", ["fix-run", "fix-out", "fix-edge"])   # 起點：while True 少冒號
        self.assertEqual(part(out, "fix-run").data.get("error"), "SyntaxError")
        self.assertIn("餵給它的輸入：120、85、q", part(out, "fix-run").detail)
        step1 = start.replace("while True\n", "while True:\n")
        write(L / "lessons/1-12/fix.py", step1)
        r = part(ev("1-12", ["fix-run"]), "fix-run")
        self.assertEqual(r.data.get("error"), "NameError")
        self.assertIn("name 'total' is not defined", r.detail)
        step2 = step1.replace("totl = 0", "total = 0")
        write(L / "lessons/1-12/fix.py", step2)
        out = ev("1-12", ["fix-run", "fix-out", "fix-edge"])
        self.assertTrue(part(out, "fix-run").ok)
        self.assertFalse(part(out, "fix-out").ok)
        self.assertIn("一共 3 筆", part(out, "fix-out").detail)   # 打 q 也算一筆
        step3 = step2.replace('    count = count + 1\n    if text == "q":\n        break\n', '    if text == "q":\n        break\n    count = count + 1\n')
        write(L / "lessons/1-12/fix.py", step3)
        out = ev("1-12", ["fix-run", "fix-out", "fix-edge"])
        self.assertEqual([r.ok for r in out.results], [True, True, False])
        self.assertIn("餵給它的輸入：120、、85、q", part(out, "fix-edge").detail)

    def test_ledger_boundaries_and_split(self):
        ids = ["ledger-q", "ledger-sum", "ledger-y80", "ledger-y100", "ledger-red", "ledger-split"]
        write(L / "lessons/1-12/ledger.py", rabbit_ledger(text("reference/ledger.py")))
        out = ev("1-12", ids)
        self.assertEqual([r.ok for r in out.results], [True, True, True, False, True, False], [r.detail for r in out.results])
        self.assertIn("紅燈", part(out, "ledger-y100").detail)
        self.assertIn("250.75", part(out, "ledger-split").detail)
        # Codex 審卷 B：剛好 80% 寫成 <=、預算寫死 1000、人數寫死 3，各自至少錯一題
        ref = text("reference/ledger.py")
        for wrong, fails in ((ref.replace("if ratio < 0.8:", "if ratio <= 0.8:"), "ledger-y80"),
                             (ref.replace("ratio = total / budget", "ratio = total / 1000"), "ledger-y80"),
                             (ref.replace("ratio = total / budget", "ratio = total / 1000"), "ledger-red"),
                             (ref.replace("total // people", "total // 3").replace("total % people", "total % 3"), "ledger-split")):
            write(L / "lessons/1-12/ledger.py", wrong)
            self.assertFalse(part(ev("1-12", [fails]), fails).ok, fails)
        wrong = ref.replace("    if kind == \"q\":\n        break\n", "")   # 沒有 break：q 被當成分類、要金額
        write(L / "lessons/1-12/ledger.py", wrong)
        self.assertFalse(part(ev("1-12", ["ledger-q"]), "ledger-q").ok)
        inside = ref.replace("food = 0\ntraffic = 0\nother = 0\nwhile True:\n", "while True:\n    food = 0\n    traffic = 0\n    other = 0\n")
        write(L / "lessons/1-12/ledger.py", inside)   # 小計每一圈都從 0 重來：一開始就打 q 還是 0，可是打 q 那一圈也歸零
        out = ev("1-12", ["ledger-q", "ledger-sum"])
        self.assertTrue(part(out, "ledger-q").ok)
        self.assertFalse(part(out, "ledger-sum").ok)
        self.assertIn("合計 0 元", part(out, "ledger-sum").detail)

    def test_tutor_form_is_filled_or_not(self):
        p = L / "lessons/1-12/tutor.md"
        out = ev("1-12", ["tutor"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("第 1 題的「家教問：」後面還空着", out.results[0].detail)
        fill_tutor(p, 2)
        self.assertIn("第 3 題的「家教問：」後面還空着", ev("1-12", ["tutor"]).results[0].detail)
        fill_tutor(p, 3)
        self.assertTrue(ev("1-12", ["tutor"]).results[0].ok)
        # 回答寫在下一行（往下接着寫）也算；「我的回答：」只寫一個問號不算
        t = p.read_text(encoding="utf-8").replace(f"我的回答：{TUTOR_QA[0][1]}", "我的回答：\n黃燈，\n因為剛好等於也成立。")
        p.write_text(t, encoding="utf-8")
        self.assertTrue(ev("1-12", ["tutor"]).results[0].ok)
        p.write_text(t.replace(f"我的回答：{TUTOR_QA[1][1]}", "我的回答：？"), encoding="utf-8")
        self.assertIn("第 2 題的「我的回答：」後面還空着", ev("1-12", ["tutor"]).results[0].detail)
        p.write_text(t.replace("## 第 3 題\n\n家教問：", "## 第 3 題\n\n"), encoding="utf-8")
        self.assertIn("找不到第 3 題的「家教問：」", ev("1-12", ["tutor"]).results[0].detail)

    def test_share_asserts_catch_the_three_broken_versions(self):
        p = L / "lessons/1-12/checks_share.py"
        out = ev("1-12", ["r3"])
        self.assertEqual([r.ok for r in out.results], [False, True, False, False, False])   # 只有範例：不夠 5 條、三個都溜過去
        base = p.read_text(encoding="utf-8")
        write(p, base + "assert share(1000, 3, 1) == 334\nassert share(1000, 3, 2) == 333\nassert share(999, 3, 3) == 333\nassert share(600, 3, 2) == 200\n")
        out = ev("1-12", ["r3"])
        self.assertEqual([r.ok for r in out.results], [True, True, True, False, False])
        self.assertTrue(any("零頭是 2 元的時候" in s for s in out.summaries), out.summaries)
        write(p, base + "assert share(1000, 3, 1) == 334\nassert share(1001, 3, 2) == 334\nassert share(1000, 4, 1) == 250\nassert share(1000, 4, 4) == 250\n")
        out = ev("1-12", ["r3"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        write(p, base + "assert share(1000, 3, 1) == 333\nassert share(1001, 3, 2) == 334\nassert share(1000, 4, 1) == 250\nassert share(1, 1, 1) == 1\n")
        r = part(ev("1-12", ["r3"]), "r3-wheat")   # 寫錯的 assert：在正確版上不成立
        self.assertFalse(r.ok)

    def test_remedial_key_matches_every_exam_check(self):
        rem = json.loads(text("remedial.json"))
        for lid in ("1-12", "1-12B"):
            les = grader.load_lesson(lid, COURSE)
            ids = [r.id for r in grader.plan(les, L) if not r.id.startswith(("tutor", "r3"))]
            self.assertEqual(sorted(ids), sorted(rem["items"]), lid)
        for t in rem["topics"].values():
            self.assertTrue((D / "practice" / t["practice"]).is_file(), t["practice"])
            for w in t["where"]:
                self.assertRegex(w["time"], r"^\d+:\d\d$")


class Flow(unittest.TestCase):
    """check.py：start、交卷、訂正、矯正包、第二三部分、卷 B、升級、status。"""

    @classmethod
    def setUpClass(cls):
        cls.home = fresh_dir("l112_home")

    def setUp(self):
        for lid in ("1-12", "1-12B"):
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
        """果凍兔卷 A：預測第 2、9 題錯、fix.py 空白的一行還算一筆、ledger.py 剛好 100% 變紅燈、每人用 / → 15／20。"""
        work = L / "lessons/1-12"
        answer("1-12", RABBIT_A)
        write(work / "parsons.py", text("reference/parsons.py"))
        write(work / "fix.py", rabbit_fix(text("reference/fix.py")))
        write(work / "ledger.py", rabbit_ledger(text("reference/ledger.py")))

    def seed_days(self, n: int) -> None:
        """之前幾課在不同天跑過檢查（練習天數）。"""
        lines = [json.dumps({"time": f"2026-11-{d:02d}T20:00:00+08:00", "lesson": "1-11", "predicted": None, "passed": 3, "total": 3, "failed": []})
                 for d in range(1, n + 1)]
        p = L / ".check/attempts.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        old = p.read_text(encoding="utf-8") if p.exists() else ""
        p.write_text("\n".join(lines) + "\n" + old, encoding="utf-8")

    def test_start_copies_only_the_exam_and_unfinished_is_not_a_submission(self):
        before = snapshot(COURSE)
        r = self.run_(["start", "1-12", "--predict", "17"], DAY1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for f in ("trace.txt", "parsons.py", "fix.py", "ledger.py"):
            self.assertIn(f"+ lessons/1-12/{f}", r.stdout)
        self.assertNotIn("tutor.md", r.stdout)
        self.assertFalse((L / "lessons/1-12/checks_share.py").exists())
        self.assertIn("關卡開始前，先寫下預測分數。", r.stdout)
        self.assertIn("記下來了：開始前你猜會過 17／20 題。交卷時會再問一次。", r.stdout)
        self.assertIn("全程關掉 AI，參考 45 分鐘（只記錄）", r.stdout)
        for line in r.stdout.splitlines():   # start 的畫面也錄進影片：70 欄寫得完
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        r = self.run_(["1-12", "--predict", "18"], DAY1)
        self.assertEqual(r.returncode, 1)
        self.assertIn("第一部分還有題目沒寫，這次先不算交卷：", r.stdout)
        self.assertIn("trace.txt 第 1、2、3、4、5、6、7、8、9 題還沒寫", r.stdout)
        self.assertIn("parsons.py 還沒改", r.stdout)
        self.assertIn("ledger.py 還沒寫程式", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertNotIn("submitted", prog["lessons"]["1-12"])
        self.assertEqual(snapshot(COURSE), before)

    def test_fail_paper_a_then_parts_two_three_and_redo(self):
        self.run_(["start", "1-12", "--predict", "17"], DAY1)
        self.rabbit_paper_a()
        touch_at("1-12", "2026-11-20T18:41:00+08:00")
        r = self.run_(["1-12", "--predict", "18", "--no-review"], "2026-11-20T18:41:30+08:00")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("結果：過了 15／20 題（16 題以上算過）", out)
        self.assertIn("  ✗ 讀程式  11／14", out)
        self.assertIn("  ✗ 從零寫 v0.1  4／6", out)
        self.assertIn("大約 41 分鐘（參考 45 分鐘，只記錄）", out)
        self.assertIn("你猜 18 題，實際過了 15 題：高估了 3 題", out)
        self.assertIn("（開始前你猜 17 題，做完猜 18 題，實際 15 題。）", out)
        self.assertIn("這次沒過。矯正包在帳本的 lessons/1-12/矯正包.md：", out)
        self.assertIn("  預測第 2 題 → 1-10 影片", out)
        self.assertIn("  錯誤訊息第 9 題 → 1-10 影片", out)
        self.assertNotIn("  修好：空白的一行 → 1-10 影片", out)   # 終端機只列前 2 題（remedial_show）
        self.assertIn("  （還有 3 題，寫在矯正包裡）", out)
        self.assertIn("練完，明天以後考卷 B：uv run check.py start 1-12B", out)
        self.assertIn("第二、三部分的檔案放進帳本了：checks_share.py、share.py、tutor.md", out)
        self.assertIn("做完再打一次 uv run check.py 1-12，檢查第二、三部分和升級。", out)
        lines = out.splitlines()
        self.assertLessEqual(len(lines), 15, out)   # 影片錄的是這一段：一個畫面 17 列（指令＋15 行＋提示字元），沒有捲動
        for line in lines:   # 70 欄寫得完（中文算兩欄）
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        pack = (L / "lessons/1-12/矯正包.md").read_text(encoding="utf-8")
        self.assertIn("正確答案：A（把第 6 行改成 total = total + int(text)）", pack)
        self.assertIn("### v0.1：剛好 100% 的燈號", pack)
        self.assertIn("1-4〈數字與運算：分帳的零頭〉", pack)
        self.assertIn("11/21 起", pack)
        self.assertEqual(sorted(p.name for p in (L / "lessons/1-12/practice").iterdir()),
                         ["p_count.py", "p_light.py", "p_q.py", "p_split.py", "p_while.py"])
        # 訂正：成績不變；第二、三部分還沒寫
        write(L / "lessons/1-12/ledger.py", text("reference/ledger.py"))
        r = self.run_(["1-12", "--no-review"], "2026-11-20T19:10:00+08:00")
        self.assertIn("第一部分（訂正）：這次過了 17／20 題；成績照 11/20 交卷算（15／20）。", r.stdout)
        self.assertIn("第二部分 家教問三題：✗ 還沒寫完", r.stdout)
        self.assertIn("第三部分 分帳的 assert：✗ 1／5", r.stdout)
        self.assertIn("升級還要：第一部分 ✗  第二部分 ✗  第三部分 ✗", r.stdout)
        fill_tutor(L / "lessons/1-12/tutor.md")
        write(L / "lessons/1-12/checks_share.py", text("answers/checks_share.py"))
        r = self.run_(["1-12", "--no-review"], "2026-11-20T19:30:00+08:00")
        self.assertIn("第二部分 家教問三題：✓ 交了", r.stdout)
        self.assertIn("第三部分 分帳的 assert：✓ 5／5", r.stdout)
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", r.stdout)
        self.assertIn("升級還要：第一部分 ✗  第二部分 ✓  第三部分 ✓", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-12"]["submitted"]["passed"], 15)
        self.assertNotIn("first_pass", prog["lessons"]["1-12"])
        self.assertEqual(sorted(prog["lessons"]["1-12"]["gate"]), ["第三部分", "第二部分"])
        # 第三部分過了以後改壞，不會倒退
        write(L / "lessons/1-12/checks_share.py", text("start_later/checks_share.py"))
        r = self.run_(["1-12", "--no-review"], "2026-11-20T19:40:00+08:00")
        self.assertIn("（11/20 就過了、記下來了；這次沒全過，不影響升級。）", r.stdout)
        rows = [json.loads(x) for x in (L / ".check/attempts.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([a["predicted"] for a in rows], [18, None, None, None])   # 訂正不問預測、不進校準曲線

    def test_paper_b_next_day_passes_and_levels_up(self):
        r = self.run_(["start", "1-12B"], DAY1)
        self.assertIn("要等卷 A 交卷以後才能考", r.stdout)
        self.run_(["start", "1-12", "--predict", "17"], DAY1)
        self.rabbit_paper_a()
        self.run_(["1-12", "--predict", "18", "--no-review"], "2026-11-20T18:41:00+08:00")
        write(L / "lessons/1-12/ledger.py", text("reference/ledger.py"))
        fill_tutor(L / "lessons/1-12/tutor.md")
        write(L / "lessons/1-12/checks_share.py", text("answers/checks_share.py"))
        self.run_(["1-12", "--no-review"], "2026-11-20T19:30:00+08:00")
        r = self.run_(["start", "1-12B", "--predict", "17"], DAY1_LATE)
        self.assertEqual(r.returncode, 1)
        self.assertIn("卷 B 要隔天以後才能考（你在 11/20 交了卷 A）", r.stdout)
        self.assertFalse((L / "lessons/1-12B").exists())
        r = self.run_(["start", "1-12-b", "--predict", "17"], DAY2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-12B/ledger.py", r.stdout)
        self.assertIn("uv run check.py 1-12B（交卷）", r.stdout)
        self.seed_days(6)
        answer("1-12B", RIGHT_B)
        for f in ("parsons.py", "fix.py"):
            write(L / "lessons/1-12B" / f, text(f"B/reference/{f}"))
        write(L / "lessons/1-12B/ledger.py", rabbit_ledger(text("B/reference/ledger.py")))
        touch_at("1-12B", "2026-11-21T19:38:00+08:00")
        r = self.run_(["1-12B", "--predict", "18", "--no-review"], "2026-11-21T19:38:30+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("結果：過了 18／20 題（16 題以上算過）", out)
        self.assertIn("你猜 18 題，實際過了 18 題：完全猜中！", out)
        self.assertIn("✓ 過了！第一部分通過。", out)
        self.assertIn("錯的那 2 題，矯正包一樣寫好了：帳本的 lessons/1-12B/矯正包.md", out)
        self.assertNotIn("警訊", out)
        self.assertIn("第二部分 家教問三題：✓ 交了", out)
        self.assertIn("第三部分 分帳的 assert：✓ 5／5", out)
        self.assertIn("★ Lv1 上 看得懂（上）過關！三部分都過了，練習了 8 天，可以升級了。", out)
        lines = out.splitlines()
        self.assertLessEqual(len(lines), 15, out)
        for line in lines:
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-12"]["passed_via"], "B")
        self.assertIn("level_up", prog["lessons"]["1-12"])
        r = self.run_(["1-12", "--no-review"], "2026-11-22T10:00:00+08:00")
        self.assertIn("第一部分：11/21 卷 B 交卷就過了（18／20）。", r.stdout)
        self.assertIn("（Lv1 上 看得懂（上）在 11/21 就過關了。）", r.stdout)
        r = self.run_(["status"], "2026-11-22T10:01:00+08:00")
        self.assertIn("✓ 1-12 Lv1 上關卡：帳本 v0.1　11/21 通過；卷 A 11/20 交卷 15／20（沒過）；卷 B 11/21 交卷 18／20", r.stdout)
        self.assertIn("第一部分✓11/21 第二部分✓11/20 第三部分✓11/20；已升級", r.stdout)
        self.assertIn("112B ", r.stdout)
        self.assertIn("1-12 交卷：開始前猜 17、做完猜 18、實際 15／20", r.stdout)

    def test_pass_paper_a_but_not_enough_days(self):
        self.run_(["start", "1-12", "--predict", "20"], DAY1)
        answer("1-12", RIGHT_A)
        for f in ("parsons.py", "fix.py", "ledger.py"):
            write(L / "lessons/1-12" / f, text(f"reference/{f}"))
        r = self.run_(["1-12", "--predict", "20", "--no-review"], "2026-11-20T18:40:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 20／20 題", r.stdout)
        self.assertIn("✓ 過了！第一部分通過。", r.stdout)
        self.assertNotIn("矯正包", r.stdout)
        fill_tutor(L / "lessons/1-12/tutor.md")
        write(L / "lessons/1-12/checks_share.py", text("answers/checks_share.py"))
        r = self.run_(["1-12", "--no-review"], "2026-11-20T19:00:00+08:00")
        self.assertIn("第一部分：11/20 卷 A 交卷就過了（20／20）。", r.stdout)
        self.assertIn("三部分都過了！練習天數 1／7 天，再練 6 天就升級", r.stdout)
        r = self.run_(["start", "1-12B"], DAY2)
        self.assertIn("卷 B 不用考", r.stdout)


if __name__ == "__main__":
    unittest.main()
