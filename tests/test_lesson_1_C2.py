"""1-C2〈檢核站 2〉：交卷、訂正、矯正包、卷 B 的回歸測試（照 test_lesson_1_C1.py；不改 check.py／grader，只測這一站的題目與流程）。

檢核站 2 跟檢核站 1 用同一套（check.py 的 cmd_checkpoint、start_checkpoint）：
  - 12 題、第一次交卷過 10 題以上算過；之後再打是訂正，不改成績；還有題目空著不算交卷（--submit 例外）。
  - 第二部分 fix.py 由 check 餵 stdin（珍奶、65元）：起點跳 TypeError，加了 int() 跳 ValueError（矯正包照錯誤種類指回原課）；
    剛好花完（300元）也要印「還在預算內」。第三部分 write.py 餵三個金額（120、剛好 500、剛好 1000）。
  - 卷 B 放在 lessons/1-C2/B/，卷 A 交卷的隔天以後才能 start；矯正包對照表卷 A、卷 B 共用（題目 id 一樣）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l1c2"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
D = COURSE / "lessons" / "1-C2"
DAY1, DAY1_LATE, DAY2 = "2026-11-18T19:00:00+08:00", "2026-11-18T23:30:00+08:00", "2026-11-19T20:00:00+08:00"
RIGHT_A = ["11月21日", "珍奶 一共 1,300 元", "B", "False True", "送一張貼紙", "A"]
RIGHT_B = ["12/05", "雞排 一共 1,200 元", "C", "False True", "全票", "C"]
FIX_A = (D / "reference" / "fix.py").read_text(encoding="utf-8")
WRITE_A = (D / "reference" / "write.py").read_text(encoding="utf-8")
START_FIX_A = (D / "start" / "fix.py").read_text(encoding="utf-8")


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def answer(lid: str, answers: list[str]) -> None:
    p = L / "lessons" / lid / "trace.txt"
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def fresh_start(lid: str = "1-C2") -> Path:
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


def rabbit_fix(text: str = START_FIX_A) -> str:
    """果凍兔的 fix.py：TypeError、ValueError 都修好了，剛好花完的 > 沒改。"""
    return text.replace('price = input("價錢：")', 'price = int(input("價錢：").replace("元", ""))')


RABBIT_WRITE = ('amount = int(input("金額："))\nif amount >= 1000:\n    fee = 0\nelif amount > 500:\n    fee = 60\nelse:\n    fee = 100\n'
                'print(f"運費 {fee} 元，一共 {amount + fee} 元")\n')


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Grading(unittest.TestCase):
    """grader：卷 A、卷 B 的正確版全過；起點的兩個錯誤種類、剛好花完、三個金額。"""

    def setUp(self):
        fresh_start("1-C2")

    def test_ids_and_paper_b_folder(self):
        info = grader.course_info(COURSE)
        for raw, want in (("1-C2", "1-C2"), ("1-c2", "1-C2"), ("1-C2B", "1-C2B"), ("1-c2b", "1-C2B"), ("1-C2-B", "1-C2B")):
            self.assertEqual(grader.normalize_id(raw, info), want, raw)
        b = grader.load_lesson("1-C2B", COURSE)
        self.assertEqual(b.dir, D / "B")
        self.assertEqual(b.meta["paper_of"], "1-C2")
        self.assertNotIn("1-C2B", grader.available_lessons(COURSE))
        self.assertIn("1-C2", grader.available_lessons(COURSE))

    def test_reference_answers_pass_all_twelve(self):
        answer("1-C2", RIGHT_A)
        write(L / "lessons/1-C2/fix.py", FIX_A)
        write(L / "lessons/1-C2/write.py", WRITE_A)
        out = ev("1-C2")
        self.assertEqual(out.total, 12)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        stages = [r.stage for r in out.results]
        self.assertEqual((stages.count("第一部分 預測輸出"), stages.count("第二部分 修好"), stages.count("第三部分 手寫")), (6, 3, 3))

    def test_paper_b_reference_passes_and_start_does_not(self):
        fresh_start("1-C2B")
        out = ev("1-C2B")
        self.assertFalse(any(r.ok for r in out.results[6:]))
        answer("1-C2B", RIGHT_B)
        write(L / "lessons/1-C2B/fix.py", (D / "B/reference/fix.py").read_text(encoding="utf-8"))
        write(L / "lessons/1-C2B/write.py", (D / "B/reference/write.py").read_text(encoding="utf-8"))
        out = ev("1-C2B")
        self.assertEqual(out.total, 12)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_trace_spacing_choices_and_common_mistakes(self):
        answer("1-C2", ["11 月 21 日", "珍奶一共1,300元", "b. 5025 和 75", "False, True", "送一張貼紙", "A. 打九折、謝謝光臨"])
        out = ev("1-C2", ["trace"])
        self.assertEqual([r.ok for r in out.results], [True] * 6, [r.detail for r in out.results])
        # 常見的錯：切到結束那一格、沒加千分位、以為 input 交回數字、剛好等於 > 也成立、elif 兩條都做、少了沒縮排那一行
        answer("1-C2", ["11月2日", "珍奶 一共 1300 元", "A", "True True", "打九折", "B"])
        out = ev("1-C2", ["trace"])
        self.assertEqual([r.ok for r in out.results], [False] * 6)
        answer("1-C2", RIGHT_A[:2] + ["5025 75"] + RIGHT_A[3:])
        r = part(ev("1-C2", ["trace"]), "trace-t3")
        self.assertFalse(r.ok)
        self.assertIn("A、B 或 C", r.detail)

    def test_fix_meets_two_error_messages_then_the_edge(self):
        out = ev("1-C2", ["fix-run", "fix-out", "fix-edge"])   # 起點：input 交回字串，budget - price 跳 TypeError
        self.assertEqual(part(out, "fix-run").data.get("error"), "TypeError")
        self.assertIn("餵給它的輸入：珍奶、65元", part(out, "fix-run").detail)
        self.assertFalse(part(out, "fix-out").ok)
        write(L / "lessons/1-C2/fix.py", START_FIX_A.replace('price = input("價錢：")', 'price = int(input("價錢："))'))
        out = ev("1-C2", ["fix-run"])
        r = part(out, "fix-run")
        self.assertEqual(r.data.get("error"), "ValueError")
        self.assertIn("'65元'", r.detail)
        write(L / "lessons/1-C2/fix.py", rabbit_fix())
        out = ev("1-C2", ["fix-run", "fix-out", "fix-edge"])
        self.assertTrue(part(out, "fix-run").ok)
        self.assertTrue(part(out, "fix-out").ok, part(out, "fix-out").detail)
        r = part(out, "fix-edge")
        self.assertFalse(r.ok)
        self.assertIn("超過預算了", r.detail)
        self.assertIn("餵給它的輸入：紅茶、300元", r.detail)

    def test_fix_out_catches_the_leftover_yuan(self):
        # 只在減法那一行 int()：跑得起來，可是印出「65元 元」
        write(L / "lessons/1-C2/fix.py", FIX_A.replace('price = int(input("價錢：").replace("元", ""))', 'price = input("價錢：")')
              .replace("left = budget - price", 'left = budget - int(price.replace("元", ""))'))
        out = ev("1-C2", ["fix-run", "fix-out", "fix-edge"])
        self.assertTrue(part(out, "fix-run").ok)
        self.assertFalse(part(out, "fix-out").ok)
        self.assertIn("65元 元", part(out, "fix-out").detail)

    def test_write_three_amounts_catch_edge_and_order(self):
        write(L / "lessons/1-C2/write.py", RABBIT_WRITE)   # 滿 500 寫成 > 500
        out = ev("1-C2", ["write-low", "write-mid", "write-top"])
        self.assertEqual([r.ok for r in out.results], [True, False, True], [r.detail for r in out.results])
        self.assertIn("運費 100 元，一共 600 元", part(out, "write-mid").detail)
        wrong_order = WRITE_A.replace("amount >= 1000", "amount >= 9999").replace("elif amount >= 500:\n    fee = 60",
                                                                                  "elif amount >= 500:\n    fee = 60\nelif amount >= 1000:\n    fee = 0")
        write(L / "lessons/1-C2/write.py", wrong_order)   # 「滿 1000」那條寫在後面：永遠輪不到
        out = ev("1-C2", ["write-low", "write-mid", "write-top"])
        self.assertEqual([r.ok for r in out.results], [True, True, False])
        write(L / "lessons/1-C2/write.py", 'print("運費 60 元，一共 710 元")\n')   # 把例子寫死
        out = ev("1-C2", ["write-low", "write-mid", "write-top"])
        self.assertEqual([r.ok for r in out.results], [False, False, False])

    def test_remedial_key_matches_every_check(self):
        rem = json.loads((D / "remedial.json").read_text(encoding="utf-8"))
        for lid in ("1-C2", "1-C2B"):
            les = grader.load_lesson(lid, COURSE)
            ids = [r.id for r in grader.plan(les, L)]
            self.assertEqual(sorted(ids), sorted(rem["items"]), lid)
        for t in rem["topics"].values():
            self.assertTrue((D / "practice" / t["practice"]).is_file(), t["practice"])
            for w in t["where"]:
                self.assertRegex(w["time"], r"^\d+:\d\d$")


class Flow(unittest.TestCase):
    """check.py：start、交卷、訂正、矯正包、卷 B、status。"""

    @classmethod
    def setUpClass(cls):
        cls.home = fresh_dir("l1c2_home")

    def setUp(self):
        for lid in ("1-C2", "1-C2B"):
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
        """果凍兔：預測第 3 題以為 input 交回數字（A）、fix.py 剛好花完的 > 沒改、write.py 滿 500 寫成 > → 9／12。"""
        work = L / "lessons/1-C2"
        answer("1-C2", RIGHT_A[:2] + ["A"] + RIGHT_A[3:])
        write(work / "fix.py", rabbit_fix((work / "fix.py").read_text(encoding="utf-8")))
        write(work / "write.py", (work / "write.py").read_text(encoding="utf-8") + RABBIT_WRITE)

    def test_start_asks_prediction_and_unfinished_is_not_a_submission(self):
        before = snapshot(COURSE)
        r = self.run_(["start", "1-C2", "--predict", "10"], DAY1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-C2/trace.txt", r.stdout)
        self.assertIn("記下來了：開始前你猜會過 10／12 題。交卷時會再問一次。", r.stdout)
        self.assertIn("參考時間 25 分鐘（只記錄，不擋你）", r.stdout)
        self.assertIn("uv run check.py 1-C2（交卷）", r.stdout)
        r = self.run_(["1-C2", "--predict", "11"], DAY1)
        self.assertEqual(r.returncode, 1)
        self.assertIn("trace.txt 第 1、2、3、4、5、6 題還沒寫", r.stdout)
        self.assertIn("fix.py 還沒改", r.stdout)
        self.assertIn("write.py 還沒寫程式", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertNotIn("submitted", prog["lessons"]["1-C2"])
        self.assertEqual(snapshot(COURSE), before)

    def test_fail_writes_the_remedial_pack_and_redo_does_not_change_the_score(self):
        self.run_(["start", "1-C2", "--predict", "10"], DAY1)
        self.rabbit_paper_a()
        r = self.run_(["1-C2", "--predict", "11", "--no-review"], "2026-11-18T19:24:00+08:00")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("結果：過了 9／12 題（10 題以上算過）", out)
        self.assertIn("✗ 第一部分 預測輸出  5／6", out)
        self.assertIn("✗ 第二部分 修好  2／3", out)
        self.assertIn("✗ 第三部分 手寫  2／3", out)
        self.assertIn("你猜 11 題，實際過了 9 題：高估了 2 題", out)
        self.assertIn("（開始前你猜 10 題，做完猜 11 題，實際 9 題。）", out)
        self.assertIn("這次沒過。矯正包在帳本的 lessons/1-C2/矯正包.md：", out)
        self.assertIn("  預測第 3 題 → 1-6 影片 3:40 起", out)
        self.assertIn("  修好：剛好花完 → 1-8 影片 1:16 起", out)
        self.assertIn("  手寫：第 2 個金額（剛好在邊界） → 1-8 影片 1:16 起", out)
        self.assertIn("練完，明天以後考卷 B：uv run check.py start 1-C2B", out)
        for line in out.splitlines():   # 影片錄的是這一段：70 欄寫得完（中文算兩欄）
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        pack = (L / "lessons/1-C2/矯正包.md").read_text(encoding="utf-8")
        self.assertIn("正確答案：B（5025 和 75）", pack)
        self.assertIn("1-8〈比較、邏輯與 assert〉1:16 起", pack)
        self.assertIn("1-9〈if／elif／else：預算燈號與 BMI〉10:46 起", pack)
        self.assertIn("11/19 起", pack)
        self.assertEqual(pack.count("### 剛好等於的那一種"), 1)   # 兩題都錯在剛好等於：同一個主題只列一次
        self.assertEqual(sorted(p.name for p in (L / "lessons/1-C2/practice").iterdir()), ["p_edge.py", "p_input.py"])
        r = self.run_(["1-C2", "--no-review"], "2026-11-18T19:40:00+08:00")
        self.assertIn("（這是訂正：成績照 11/18 第一次交卷算，過了 9／12 題。）", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-C2"]["submitted"]["passed"], 9)
        self.assertNotIn("first_pass", prog["lessons"]["1-C2"])
        rows = [json.loads(x) for x in (L / ".check/attempts.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([a["predicted"] for a in rows], [11, None])   # 訂正不問預測、不進校準曲線

    def test_crash_points_the_pack_by_error_kind(self):
        self.run_(["start", "1-C2", "--predict", "6"], DAY1)
        answer("1-C2", RIGHT_A)
        work = L / "lessons/1-C2"
        write(work / "fix.py", START_FIX_A.replace('price = input("價錢：")', 'price = int(input("價錢："))'))   # 停在 ValueError
        write(work / "write.py", (work / "write.py").read_text(encoding="utf-8") + WRITE_A)
        r = self.run_(["1-C2", "--predict", "9", "--no-review"], "2026-11-18T19:20:00+08:00")
        self.assertIn("結果：過了 9／12 題", r.stdout)
        self.assertIn("  修好：跑不起來（ValueError） → 1-6 影片 6:41 起", r.stdout)
        pack = (L / "lessons/1-C2/矯正包.md").read_text(encoding="utf-8")
        self.assertIn("ValueError：int() 看不懂的字", pack)
        self.assertTrue((work / "practice" / "p_value_error.py").is_file())

    def test_paper_b_waits_for_the_next_day_and_passing_b_passes_the_checkpoint(self):
        r = self.run_(["start", "1-C2B"], DAY1)
        self.assertIn("要等卷 A 交卷以後才能考", r.stdout)
        self.run_(["start", "1-C2", "--predict", "10"], DAY1)
        self.rabbit_paper_a()
        self.run_(["1-C2", "--predict", "11", "--no-review"], "2026-11-18T19:24:00+08:00")
        r = self.run_(["start", "1-C2B", "--predict", "10"], DAY1_LATE)
        self.assertEqual(r.returncode, 1)
        self.assertIn("卷 B 要隔天以後才能考（你在 11/18 交了卷 A）", r.stdout)
        self.assertFalse((L / "lessons/1-C2B").exists())
        r = self.run_(["start", "1-c2b", "--predict", "10"], DAY2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-C2B/write.py", r.stdout)
        answer("1-C2B", RIGHT_B)
        write(L / "lessons/1-C2B/fix.py", (D / "B/reference/fix.py").read_text(encoding="utf-8").replace("spent <= budget", "spent < budget"))
        write(L / "lessons/1-C2B/write.py", (D / "B/reference/write.py").read_text(encoding="utf-8"))
        r = self.run_(["1-C2B", "--predict", "11", "--no-review"], "2026-11-19T20:22:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 11／12 題（10 題以上算過）", r.stdout)
        self.assertIn("✓ 過了！檢核站 2 通過。", r.stdout)
        self.assertIn("錯的那 1 題，矯正包一樣寫好了：帳本的 lessons/1-C2B/矯正包.md", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-C2"]["passed_via"], "B")
        r = self.run_(["status"], "2026-11-19T20:25:00+08:00")
        self.assertIn("✓ 1-C2 檢核站 2　11/19 通過；卷 A 11/18 交卷 9／12（沒過）；卷 B 11/19 交卷 11／12", r.stdout)
        self.assertIn("1C2B ", r.stdout)
        self.assertIn("1-C2 交卷：開始前猜 10、做完猜 11、實際 9／12", r.stdout)

    def test_pass_on_paper_a_and_submit_flag(self):
        self.run_(["start", "1-C2", "--predict", "12"], DAY1)
        answer("1-C2", RIGHT_A[:5] + [""])
        write(L / "lessons/1-C2/fix.py", FIX_A)
        write(L / "lessons/1-C2/write.py", WRITE_A)
        r = self.run_(["1-C2", "--predict", "12", "--no-review"], "2026-11-18T19:15:00+08:00")
        self.assertIn("trace.txt 第 6 題還沒寫", r.stdout)
        r = self.run_(["1-C2", "--predict", "12", "--submit", "--no-review"], "2026-11-18T19:15:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 11／12 題", r.stdout)
        self.assertIn("✓ 過了！檢核站 2 通過。", r.stdout)
        r = self.run_(["start", "1-C2B"], DAY2)
        self.assertIn("就過了檢核站 2，卷 B 不用考", r.stdout)


if __name__ == "__main__":
    unittest.main()
