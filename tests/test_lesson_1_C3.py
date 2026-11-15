"""1-C3〈檢核站 3〉：交卷、訂正、矯正包、卷 B 的回歸測試（照 test_lesson_1_C2.py；不改 check.py／grader，只測這一站的題目與流程）。

檢核站 3 跟檢核站 1、2 用同一套（check.py 的 cmd_checkpoint、start_checkpoint）：
  - 11 題、第一次交卷過 9 題以上算過；之後再打是訂正，不改成績；還有題目空著不算交卷（--submit 例外）。
  - 第一部分 trace.txt 追蹤 6 題（選擇題 strict_choice、一行印好幾個值的 keep_spaces）；第二部分 parsons.py 拼圖 2 題（parsons）；
    第三部分 write.py 依分類加總 3 題：每一題用 runs 換兩組帳（swap 換掉 records 那一行），一組在中間的、一組在邊界的。
  - 卷 B 放在 lessons/1-C3/B/，卷 A 交卷的隔天以後才能 start；矯正包對照表卷 A、卷 B 共用（題目 id 一樣）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import json
import os
import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l1c3"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
D = COURSE / "lessons" / "1-C3"
DAY1, DAY1_LATE, DAY2 = "2026-11-25T19:00:00+08:00", "2026-11-25T23:30:00+08:00", "2026-11-26T20:00:00+08:00"
RIGHT_A = ["[120, 45, 300, 60]", "[45, 300]", "2 3", "C", "4 100 0", "A"]
RIGHT_B = ["[50, 80, 200, 35]", "[80, 35]", "3 4", "A", "3 120 0", "C"]
PZ_A = (D / "reference" / "parsons.py").read_text(encoding="utf-8")
WRITE_A = (D / "reference" / "write.py").read_text(encoding="utf-8")
START_WRITE_A = (D / "start" / "write.py").read_text(encoding="utf-8")
DATA_A = 'records = [("早餐", 60), ("午餐", 120), ("早餐", 45), ("飲料", 65), ("午餐", 90)]\n'
WRITE_IDS = ["write-one", "write-sum", "write-new"]
REM = json.loads((D / "remedial.json").read_text(encoding="utf-8"))
T_SORT = REM["topics"]["sort"]["where"][0]["time"]      # 1-13 排序那一章（時間碼照各課說明欄，那幾課重剪就會變，測試照 remedial.json 比）
T_TOT = REM["topics"]["totals"]["where"][0]["time"]     # 1-15 各分類的小計那一章

# 第三部分常見的寫法（接在 records 那一行後面）：對的兩種、寫錯的幾種
BODY = {
    "if_in": ("totals = {}\nfor kind, amount in records:\n    if kind in totals:\n        totals[kind] = totals[kind] + amount\n"
              "    else:\n        totals[kind] = amount\nfor kind in totals:\n    print(kind, totals[kind], \"元\")\n"),
    "list_kinds": ("kinds = []\nfor kind, amount in records:\n    if kind not in kinds:\n        kinds.append(kind)\nfor k in kinds:\n"
                   "    total = 0\n    for kind, amount in records:\n        if kind == k:\n            total = total + amount\n    print(k, total, \"元\")\n"),
    "overwrite": "totals = {}\nfor kind, amount in records:\n    totals[kind] = amount\nfor kind, total in totals.items():\n    print(kind, total, \"元\")\n",
    "print_in_loop": "totals = {}\nfor kind, amount in records:\n    totals[kind] = totals.get(kind, 0) + amount\n    print(kind, totals[kind], \"元\")\n",
    "hardcode": ("b = 0\nl = 0\nd = 0\nfor kind, amount in records:\n    if kind == \"早餐\":\n        b = b + amount\n    elif kind == \"午餐\":\n"
                 "        l = l + amount\n    else:\n        d = d + amount\nprint(\"早餐\", b, \"元\")\nprint(\"午餐\", l, \"元\")\nprint(\"飲料\", d, \"元\")\n"),
    "first_record": ("totals = {records[0][0]: 0}\nfor kind, amount in records:\n    totals[kind] = totals.get(kind, 0) + amount\n"
                     "for kind, total in totals.items():\n    print(kind, total, \"元\")\n"),
    "sorted": ("totals = {}\nfor kind, amount in records:\n    totals[kind] = totals.get(kind, 0) + amount\nfor kind in sorted(totals):\n"
               "    print(kind, totals[kind], \"元\")\n"),
    "keyerror": "totals = {}\nfor kind, amount in records:\n    totals[kind] = totals[kind] + amount\nfor kind in totals:\n    print(kind, totals[kind], \"元\")\n",
    # Codex 審卷 B 抓到的兩種：只算前五筆（原本每一組最多五筆）、用 set 決定印的順序（照 hash 的種子有時剛好對）
    "first_five": ("totals = {}\nfor kind, amount in records[:5]:\n    totals[kind] = totals.get(kind, 0) + amount\n"
                   "for kind, total in totals.items():\n    print(kind, total, \"元\")\n"),
    "set_order": ("totals = {}\nfor kind, amount in records:\n    totals[kind] = totals.get(kind, 0) + amount\nfor kind in set(totals):\n"
                  "    print(kind, totals[kind], \"元\")\n"),
}


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def answer(lid: str, answers: list[str]) -> None:
    p = L / "lessons" / lid / "trace.txt"
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def fresh_start(lid: str = "1-C3") -> Path:
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


def oks(out: grader.Outcome) -> list[bool]:
    return [r.ok for r in out.results]


RABBIT_WRITE = BODY["overwrite"]   # 果凍兔：同一類又遇到一次，金額直接換掉（沒有加起來）


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Grading(unittest.TestCase):
    """grader：卷 A、卷 B 的正確版全過、起點不過；追蹤題的寫法與常見的錯；拼圖；手寫三題換兩組帳。"""

    def setUp(self):
        fresh_start("1-C3")

    def test_ids_and_paper_b_folder(self):
        info = grader.course_info(COURSE)
        for raw, want in (("1-C3", "1-C3"), ("1-c3", "1-C3"), ("1-C3B", "1-C3B"), ("1-c3b", "1-C3B"), ("1-C3-B", "1-C3B")):
            self.assertEqual(grader.normalize_id(raw, info), want, raw)
        b = grader.load_lesson("1-C3B", COURSE)
        self.assertEqual(b.dir, D / "B")
        self.assertEqual(b.meta["paper_of"], "1-C3")
        self.assertNotIn("1-C3B", grader.available_lessons(COURSE))
        self.assertIn("1-C3", grader.available_lessons(COURSE))

    def test_reference_answers_pass_all_eleven_and_start_does_not(self):
        out = ev("1-C3")
        self.assertEqual(out.total, 11)
        self.assertFalse(any(r.ok for r in out.results[6:]), [(r.id, r.ok) for r in out.results])
        answer("1-C3", RIGHT_A)
        write(L / "lessons/1-C3/parsons.py", PZ_A)
        write(L / "lessons/1-C3/write.py", WRITE_A)
        out = ev("1-C3")
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        stages = [r.stage for r in out.results]
        self.assertEqual((stages.count("第一部分 追蹤"), stages.count("第二部分 拼圖"), stages.count("第三部分 手寫")), (6, 2, 3))

    def test_paper_b_reference_passes_and_start_does_not(self):
        fresh_start("1-C3B")
        out = ev("1-C3B")
        self.assertFalse(any(r.ok for r in out.results[6:]))
        answer("1-C3B", RIGHT_B)
        write(L / "lessons/1-C3B/parsons.py", (D / "B/reference/parsons.py").read_text(encoding="utf-8"))
        write(L / "lessons/1-C3B/write.py", (D / "B/reference/write.py").read_text(encoding="utf-8"))
        out = ev("1-C3B")
        self.assertEqual(out.total, 11)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_trace_spacing_choices_and_common_mistakes(self):
        answer("1-C3", ["[120,45,300,60]", "[ 45, 300 ]", "2 3", "c. None [50, 90, 120]", "4  100  0", "A. [120, 300]"])
        out = ev("1-C3", ["trace"])
        self.assertEqual(oks(out), [True] * 6, [r.detail for r in out.results])
        # 常見的錯：以為 b = a 是複製、以為 copy 以後還連在一起、set 沒去重複、以為 sort() 交回排好的、dict 加錯、以為改 dict 會改到 list
        answer("1-C3", ["[120, 45, 300]", "[45, 300, 60]", "3 3", "A", "4 80 0", "B"])
        self.assertEqual(oks(ev("1-C3", ["trace"])), [False] * 6)
        # keep_spaces：「2 3」寫成「23」、「4 100 0」寫成「41000」不算對
        answer("1-C3", RIGHT_A[:2] + ["23"] + RIGHT_A[3:4] + ["41000"] + RIGHT_A[5:])
        out = ev("1-C3", ["trace"])
        self.assertFalse(part(out, "trace-t3").ok)
        self.assertFalse(part(out, "trace-t5").ok)
        # strict_choice：同時寫兩個字母不算選了正確的那一個
        answer("1-C3", RIGHT_A[:3] + ["C 或 A"] + RIGHT_A[4:5] + ["A、B"])
        out = ev("1-C3", ["trace"])
        self.assertFalse(part(out, "trace-t4").ok)
        self.assertIn("只能選一個", part(out, "trace-t4").detail)
        self.assertFalse(part(out, "trace-t6").ok)

    def test_parsons_order_and_run(self):
        lines = PZ_A.splitlines()[1:]   # 拿掉第一行說明
        # 兩行在 if 底下誰先誰後都可以
        swapped = "\n".join(lines[:4] + [lines[5], lines[4]] + lines[6:]) + "\n"
        write(L / "lessons/1-C3/parsons.py", swapped)
        self.assertEqual(oks(ev("1-C3", ["pz"])), [True, True])
        # append 縮在 for 底下（沒在 if 底下）：Python 讀得懂，可是一共 4 天
        loose = PZ_A.replace("        over.append(a)", "    over.append(a)")
        write(L / "lessons/1-C3/parsons.py", loose)
        out = ev("1-C3", ["pz"])
        self.assertEqual(oks(out), [True, False])
        self.assertIn("一共 4 天超過 100 元", part(out, "pz-run").detail)
        # 一共幾天那一行縮進 for 底下：每一天都印一次
        write(L / "lessons/1-C3/parsons.py", PZ_A.replace('print("一共"', '    print("一共"'))
        self.assertEqual(oks(ev("1-C3", ["pz"])), [True, False])
        # 改了字（> 改成 >=）、少一行：order 不過，run 也不看
        write(L / "lessons/1-C3/parsons.py", PZ_A.replace("a > 100", "a >= 100"))
        out = ev("1-C3", ["pz"])
        self.assertEqual(oks(out), [False, False])
        self.assertIn("不是拼圖裡的行", part(out, "pz-order").detail)
        write(L / "lessons/1-C3/parsons.py", PZ_A.replace("over = []\n", ""))
        out = ev("1-C3", ["pz"])
        self.assertIn("少了「over = []」這一行", part(out, "pz-order").detail)
        # 沒縮排（起點檔的樣子排好了順序）：Python 讀不懂
        write(L / "lessons/1-C3/parsons.py", "\n".join(ln.strip() for ln in lines) + "\n")
        out = ev("1-C3", ["pz"])
        self.assertFalse(part(out, "pz-order").ok)
        self.assertIn("縮排不對", part(out, "pz-order").detail)

    def test_write_two_data_sets_per_question(self):
        def grade(body: str) -> list[bool]:
            write(L / "lessons/1-C3/write.py", DATA_A + body)
            return oks(ev("1-C3", WRITE_IDS))
        self.assertEqual(grade(BODY["if_in"]), [True, True, True])
        self.assertEqual(grade(BODY["list_kinds"]), [True, True, True])   # 不用 dict 也可以：只看印出來的字
        self.assertEqual(grade(BODY["overwrite"]), [True, False, False])
        self.assertEqual(grade(BODY["print_in_loop"]), [True, False, False])   # 每一類只有一筆時剛好對：中間那組才抓得到
        self.assertEqual(grade(BODY["hardcode"]), [False, False, False])
        self.assertEqual(grade(BODY["first_record"]), [True, True, False])    # 一筆都沒有時拿第 0 筆：只有邊界那組抓得到
        self.assertEqual(grade(BODY["sorted"]), [False, False, False])         # 題目要照第一次出現的順序
        self.assertEqual(grade(BODY["keyerror"]), [False, False, False])
        self.assertEqual(grade(BODY["first_five"]), [True, True, False])     # 七筆那一組才抓得到（Codex 審卷 B）
        write(L / "lessons/1-C3/write.py", DATA_A + BODY["overwrite"])
        r = part(ev("1-C3", ["write-sum"]), "write-sum")
        self.assertIn("早餐 45 元", r.detail)   # 中間那組（題目的帳）就錯了
        write(L / "lessons/1-C3/write.py", DATA_A + BODY["first_record"])
        r = part(ev("1-C3", ["write-new"]), "write-new")
        self.assertIn("check 把你的 records 換成 []（一筆都沒有）", r.detail)
        self.assertIn("IndexError", r.detail)
        # 把例子寫死、records 拆成好幾行
        write(L / "lessons/1-C3/write.py", DATA_A + 'print("早餐 105 元")\nprint("午餐 210 元")\nprint("飲料 65 元")\n')
        self.assertEqual(oks(ev("1-C3", WRITE_IDS)), [False, False, False])
        write(L / "lessons/1-C3/write.py", 'records = [\n    ("早餐", 60),\n    ("午餐", 120),\n]\n' + BODY["if_in"])
        r = part(ev("1-C3", ["write-one"]), "write-one")
        self.assertIn("找不到 records = [...] 這一行", r.detail)

    def test_paper_b_write_catches_the_same_mistakes(self):
        fresh_start("1-C3B")
        data = 'pays = [("現金", 120), ("悠遊卡", 30), ("現金", 85), ("信用卡", 990), ("悠遊卡", 45)]\n'
        hard = ('a = 0\nb = 0\nc = 0\nfor way, amount in pays:\n    if way == "現金":\n        a = a + amount\n    elif way == "悠遊卡":\n'
                '        b = b + amount\n    else:\n        c = c + amount\nprint("現金", a, "元")\nprint("悠遊卡", b, "元")\nprint("信用卡", c, "元")\n')
        for name, want in (("if_in", [True, True, True]), ("list_kinds", [True, True, True]), ("overwrite", [True, False, False]),
                           ("print_in_loop", [True, False, False]), ("first_record", [True, True, False]), ("sorted", [False, False, False]),
                           ("keyerror", [False, False, False]), ("first_five", [True, True, False])):
            write(L / "lessons/1-C3B/write.py", data + BODY[name].replace("records", "pays"))
            self.assertEqual(oks(ev("1-C3B", WRITE_IDS)), want, name)
        write(L / "lessons/1-C3B/write.py", data + hard)
        self.assertEqual(oks(ev("1-C3B", WRITE_IDS)), [False, False, False])

    def test_set_order_never_gets_all_three_with_a_fixed_seed(self):
        # 用 set 決定印的順序：同樣四個鍵跑三種第一次出現的順序（每一類只有一筆兩組、沒看過的分類一組），種子固定時至少錯一組（Codex 審卷 B 兩輪：
        # 5618 是第二輪找到的、只有兩種順序時卷 B 會全對的種子；2021、9186、9601 是兩種順序時模擬找到的；10000 個固定種子模擬三種順序 0 次全對）
        old = os.environ.get("PYTHONHASHSEED")
        try:
            for lid, var, data in (("1-C3", "records", DATA_A), ("1-C3B", "pays", 'pays = [("現金", 120), ("悠遊卡", 30), ("現金", 85), ("信用卡", 990), ("悠遊卡", 45)]\n')):
                fresh_start(lid)
                write(L / "lessons" / lid / "write.py", data + BODY["set_order"].replace("records", var))
                for seed in ("0", "128", "177", "254", "5618", "2021", "9186", "9601"):
                    os.environ["PYTHONHASHSEED"] = seed   # child_env 照抄 os.environ：每一次跑學員程式都用同一個種子
                    self.assertFalse(all(oks(ev(lid, WRITE_IDS))), (lid, seed))
        finally:
            if old is None:
                os.environ.pop("PYTHONHASHSEED", None)
            else:
                os.environ["PYTHONHASHSEED"] = old

    def test_paper_b_trace_and_parsons_common_mistakes(self):
        fresh_start("1-C3B")
        answer("1-C3B", ["[50,80,200,35]", "[80, 35]", "3  4", "a. None [15, 15, 25, 180]", "3 120 0", "C"])
        self.assertEqual(oks(ev("1-C3B", ["trace"])), [True] * 6)
        # 以為 z = x 是複製、以為 copy 以後還連在一起、set 沒去重複、以為 sort() 交回排好的、以為 get 查不到會出錯、以為改 dict 會改到 list
        answer("1-C3B", ["[80, 200, 35]", "[50, 80, 35]", "4 4", "B", "3 150 0", "A"])
        self.assertEqual(oks(ev("1-C3B", ["trace"])), [False] * 6)
        answer("1-C3B", RIGHT_B[:2] + ["34"] + RIGHT_B[3:4] + ["31200"] + ["C 或 A"])
        out = ev("1-C3B", ["trace"])
        self.assertEqual([part(out, x).ok for x in ("trace-t3", "trace-t5", "trace-t6")], [False, False, False])
        pz = (D / "B/reference/parsons.py").read_text(encoding="utf-8")
        write(L / "lessons/1-C3B/parsons.py", pz)
        self.assertEqual(oks(ev("1-C3B", ["pz"])), [True, True])
        write(L / "lessons/1-C3B/parsons.py", pz.replace("        taxi.append(f)", "    taxi.append(f)"))
        out = ev("1-C3B", ["pz"])
        self.assertEqual(oks(out), [True, False])
        self.assertIn("一共 4 趟 100 元以上", part(out, "pz-run").detail)
        write(L / "lessons/1-C3B/parsons.py", pz.replace("f >= 100", "f > 100"))
        self.assertEqual(oks(ev("1-C3B", ["pz"])), [False, False])

    def test_remedial_key_matches_every_check(self):
        rem = json.loads((D / "remedial.json").read_text(encoding="utf-8"))
        for lid in ("1-C3", "1-C3B"):
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
        cls.home = fresh_dir("l1c3_home")

    def setUp(self):
        for lid in ("1-C3", "1-C3B"):
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
        """果凍兔：追蹤第 4 題以為 sort() 交回排好的（A）、拼圖排對、write.py 同一類沒有加起來 → 8／11。"""
        work = L / "lessons/1-C3"
        answer("1-C3", RIGHT_A[:3] + ["A"] + RIGHT_A[4:])
        write(work / "parsons.py", PZ_A)
        write(work / "write.py", (work / "write.py").read_text(encoding="utf-8") + RABBIT_WRITE)

    def test_start_asks_prediction_and_unfinished_is_not_a_submission(self):
        before = snapshot(COURSE)
        r = self.run_(["start", "1-C3", "--predict", "9"], DAY1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-C3/parsons.py", r.stdout)
        self.assertIn("記下來了：開始前你猜會過 9／11 題。交卷時會再問一次。", r.stdout)
        self.assertIn("參考時間 25 分鐘（只記錄，不擋你）", r.stdout)
        self.assertIn("uv run check.py 1-C3（交卷）", r.stdout)
        for line in r.stdout.splitlines():   # 影片錄的是這一段：70 欄寫得完（中文算兩欄）
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        r = self.run_(["1-C3", "--predict", "10"], DAY1)
        self.assertEqual(r.returncode, 1)
        self.assertIn("trace.txt 第 1、2、3、4、5、6 題還沒寫", r.stdout)
        self.assertIn("parsons.py 還沒改", r.stdout)
        self.assertIn("write.py 還沒改", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertNotIn("submitted", prog["lessons"]["1-C3"])
        self.assertEqual(snapshot(COURSE), before)

    def test_fail_writes_the_remedial_pack_and_redo_does_not_change_the_score(self):
        self.run_(["start", "1-C3", "--predict", "9"], DAY1)
        self.rabbit_paper_a()
        r = self.run_(["1-C3", "--predict", "10", "--no-review"], "2026-11-25T19:24:00+08:00")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("結果：過了 8／11 題（9 題以上算過）", out)
        self.assertIn("✗ 第一部分 追蹤  5／6", out)
        self.assertIn("✓ 第二部分 拼圖  2／2", out)
        self.assertIn("✗ 第三部分 手寫  1／3", out)
        self.assertIn("你猜 10 題，實際過了 8 題：高估了 2 題", out)
        self.assertIn("（開始前你猜 9 題，做完猜 10 題，實際 8 題。）", out)
        self.assertIn("這次沒過。矯正包在帳本的 lessons/1-C3/矯正包.md：", out)
        self.assertIn(f"  追蹤第 4 題 → 1-13 影片 {T_SORT} 起", out)
        self.assertIn(f"  手寫：同一類有好幾筆 → 1-15 影片 {T_TOT} 起", out)
        self.assertIn(f"  手寫：沒看過的分類、一筆都沒有 → 1-15 影片 {T_TOT} 起", out)
        self.assertIn("練完，明天以後考卷 B：uv run check.py start 1-C3B", out)
        self.assertLessEqual(len(out.splitlines()), 16)   # 影片錄的是這一段：一個畫面 17 列（含指令那一列）
        for line in out.splitlines():
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        readme = (D / "README.md").read_text(encoding="utf-8")
        for line in out.splitlines()[1:]:   # README 第 4 節的成品示範跟真的印出來的一樣
            if line.strip() and "大約" not in line:
                self.assertIn(line, readme)
        pack = (L / "lessons/1-C3/矯正包.md").read_text(encoding="utf-8")
        self.assertIn("正確答案：C（None [50, 90, 120]）", pack)
        self.assertIn(f"1-15〈dict：用名字找資料〉{T_TOT} 起", pack)
        self.assertIn(f"1-13〈list：一串帳目〉{T_SORT} 起", pack)
        self.assertIn("11/26 起", pack)
        self.assertEqual(pack.count("### 依分類加總"), 1)   # 兩題都錯在同一類沒有加起來：同一個主題只列一次
        self.assertEqual(sorted(p.name for p in (L / "lessons/1-C3/practice").iterdir()), ["p_sort.py", "p_totals.py"])
        r = self.run_(["1-C3", "--no-review"], "2026-11-25T19:40:00+08:00")
        self.assertIn("（這是訂正：成績照 11/25 第一次交卷算，過了 8／11 題。）", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-C3"]["submitted"]["passed"], 8)
        self.assertNotIn("first_pass", prog["lessons"]["1-C3"])
        rows = [json.loads(x) for x in (L / ".check/attempts.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([a["predicted"] for a in rows], [10, None])   # 訂正不問預測、不進校準曲線

    def test_paper_b_waits_for_the_next_day_and_passing_b_passes_the_checkpoint(self):
        r = self.run_(["start", "1-C3B"], DAY1)
        self.assertIn("要等卷 A 交卷以後才能考", r.stdout)
        self.run_(["start", "1-C3", "--predict", "9"], DAY1)
        self.rabbit_paper_a()
        self.run_(["1-C3", "--predict", "10", "--no-review"], "2026-11-25T19:24:00+08:00")
        r = self.run_(["start", "1-C3B", "--predict", "9"], DAY1_LATE)
        self.assertEqual(r.returncode, 1)
        self.assertIn("卷 B 要隔天以後才能考（你在 11/25 交了卷 A）", r.stdout)
        self.assertFalse((L / "lessons/1-C3B").exists())
        r = self.run_(["start", "1-c3b", "--predict", "9"], DAY2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-C3B/write.py", r.stdout)
        answer("1-C3B", RIGHT_B[:5] + ["A"])
        write(L / "lessons/1-C3B/parsons.py", (D / "B/reference/parsons.py").read_text(encoding="utf-8"))
        write(L / "lessons/1-C3B/write.py", (D / "B/reference/write.py").read_text(encoding="utf-8"))
        r = self.run_(["1-C3B", "--predict", "10", "--no-review"], "2026-11-26T20:22:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 10／11 題（9 題以上算過）", r.stdout)
        self.assertIn("✓ 過了！檢核站 3 通過。", r.stdout)
        self.assertIn("錯的那 1 題，矯正包一樣寫好了：帳本的 lessons/1-C3B/矯正包.md", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-C3"]["passed_via"], "B")
        r = self.run_(["status"], "2026-11-26T20:25:00+08:00")
        self.assertIn("✓ 1-C3 檢核站 3　11/26 通過；卷 A 11/25 交卷 8／11（沒過）；卷 B 11/26 交卷 10／11", r.stdout)
        self.assertIn("1C3B ", r.stdout)
        self.assertIn("1-C3 交卷：開始前猜 9、做完猜 10、實際 8／11", r.stdout)

    def test_pass_on_paper_a_and_submit_flag(self):
        self.run_(["start", "1-C3", "--predict", "11"], DAY1)
        answer("1-C3", RIGHT_A[:5] + [""])
        write(L / "lessons/1-C3/parsons.py", PZ_A)
        write(L / "lessons/1-C3/write.py", WRITE_A)
        r = self.run_(["1-C3", "--predict", "11", "--no-review"], "2026-11-25T19:15:00+08:00")
        self.assertIn("trace.txt 第 6 題還沒寫", r.stdout)
        r = self.run_(["1-C3", "--predict", "11", "--submit", "--no-review"], "2026-11-25T19:15:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 10／11 題", r.stdout)
        self.assertIn("✓ 過了！檢核站 3 通過。", r.stdout)
        r = self.run_(["start", "1-C3B"], DAY2)
        self.assertIn("就過了檢核站 3，卷 B 不用考", r.stdout)


if __name__ == "__main__":
    unittest.main()
