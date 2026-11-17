"""1-27〈Lv1 下關卡：帳本 v1.0＋看得懂進度條 100%〉：考卷（追蹤、白話、拼圖、找 bug、手寫帳本 v1.0）、第二部分（自評，不擋升級）、
第三部分（每月預算設定：docstring＋assert 抓 3 個壞版本）、升級（滿 14 天）的回歸測試。

1-27 照 1-12 的「有考卷的關卡」（check.py 的 cmd_exam_gate）：
  - 第一部分 20 題（讀程式 14、手寫 6），第一次交卷過 16 題以上算過；之後再打是訂正；沒過領矯正包，隔天以後考卷 B（lessons/1-27/B/）。
  - 第二部分 explain.md 是自評，lesson.json 的 gate_parts 標 optional（1-27 在 check.py 加的欄位，只對寫了它的關卡生效）：
    寫了記下來，沒寫不擋升級（總企劃第七節：自評只記錄、不擋升級；課表 1-27：①③都過、練習滿 14 天升級）。
  - 第三部分 budget.py 的 docstring（func_shape）＋checks_budget.py（chaff 的 assert 模式加 try_checks）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import unittest
from datetime import datetime
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l127"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
D = COURSE / "lessons" / "1-27"
DAY1 = "2026-11-20T18:00:00+08:00"
RIGHT_A = {"trace": ["350 80", "2 0", "2 電影", "電影 15", "跳過 八十", "2 155"], "plain": ["C", "B", "A"]}
RIGHT_B = {"trace": ["75 120", "2 10", "2 週一", "週三 260", "跳過 兩百", "2 105"], "plain": ["B", "A", "B"]}
EXAM_FILES = ("trace.txt", "plain.txt", "parsons.py", "fix.py", "ledger_v1.py")


def text(rel: str) -> str:
    return (D / rel).read_text(encoding="utf-8")


def write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.encode("utf-8"))
    return path


def cells(line: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in line)


def answer(lid: str, name: str, answers: list[str]) -> None:
    p = L / "lessons" / lid / name
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def fresh_start(lid: str = "1-27", later: bool = False) -> Path:
    dest = L / "lessons" / lid
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(D / ("B/start" if lid.endswith("B") else "start"), dest)
    if later:
        shutil.copytree(D / "start_later", dest, dirs_exist_ok=True)
    return dest


def all_right(lid: str = "1-27") -> None:
    src = D / ("B" if lid.endswith("B") else "")
    right = RIGHT_B if lid.endswith("B") else RIGHT_A
    answer(lid, "trace.txt", right["trace"])
    answer(lid, "plain.txt", right["plain"])
    for f in ("parsons.py", "fix.py", "ledger_v1.py"):
        write(L / "lessons" / lid / f, (src / "reference" / f).read_text(encoding="utf-8"))


def ev(lid: str, ids: list[str] | None = None) -> grader.Outcome:
    les = grader.load_lesson(lid, COURSE)
    return grader.evaluate(les, L, only=None if ids is None else [c for c in les.checks if c["id"] in ids])


def oks(out: grader.Outcome) -> dict[str, bool]:
    return {r.id: r.ok for r in out.results}


# 熊的卷 A（影片 t02，情境重現）：追蹤第 4 題以為 top[-1][1] 是 280、fix.py 沒發現預設值 [] 共用、save 用了 "a" → 17／20
BEAR_TRACE = ["350 80", "2 0", "2 電影", "電影 280", "跳過 八十", "2 155"]


def bear_fix(src: str) -> str:
    """熊的 fix.py：月份改成 startswith、biggest 的比較改好，預設值 picked=[] 沒發現。"""
    return src.replace("        if month in e.date:", '        if e.date.startswith(month + "/"):').replace("if e.amount < best.amount:", "if e.amount > best.amount:")


def bear_ledger(src: str) -> str:
    """熊的 ledger_v1.py：save 用了 "a"（接在後面），其他都對。"""
    out = src.replace('    with open(path, "w", encoding="utf-8") as f:', '    with open(path, "a", encoding="utf-8") as f:')
    assert out != src
    return out


EXPLAIN = {"我講的函式：": "load", "怎麼講的：": "錄音 3 分鐘", "它收什麼、交回什麼：": "2", "照執行的順序一行一行講：": "2",
           "舉一個例子，算出交回什麼：": "1", "一個特別的情況會怎樣：": "2", "為什麼這樣寫：": "1"}
DOC = '''    """設定某個月的預算。

    輸入：budgets 是放每個月預算的 dict；month 像 "2026-11"；text 是打進來的金額
    輸出：設定好的預算（整數）
    規則：月要在 01 到 12，金額拿掉逗號和元以後要大於 0；不合法丟 ValueError、budgets 不改；同一個月再設一次蓋掉
    例子：set_budget(b, "2026-11", "8,000元") 交回 8000
    """'''


def fill_explain(path: Path, skip: str | None = None) -> None:
    lines = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln in EXPLAIN and ln != skip:
            ln += EXPLAIN[ln]
        lines.append(ln)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fill_doc(path: Path, doc: str = DOC) -> None:
    s = path.read_text(encoding="utf-8")
    start = s.index('    """設定某個月的預算。')
    end = s.index('    """', start + 10) + len('    """')
    path.write_text(s[:start] + doc + s[end:], encoding="utf-8")


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Grading(unittest.TestCase):
    """grader：卷 A、卷 B 的正確版全過；起點檔、三個 bug 各自獨立、v1.0 常見的錯、第二部分、第三部分的壞版本。"""

    def setUp(self):
        fresh_start("1-27", later=True)

    def test_ids_meta_and_paper_b_folder(self):
        info = grader.course_info(COURSE)
        for raw, want in (("1-27", "1-27"), ("1-27B", "1-27B"), ("1-27b", "1-27B"), ("1-27-B", "1-27B")):
            self.assertEqual(grader.normalize_id(raw, info), want, raw)
        b = grader.load_lesson("1-27B", COURSE)
        self.assertEqual(b.dir, D / "B")
        self.assertEqual(b.meta["paper_of"], "1-27")
        a = grader.load_lesson("1-27", COURSE)
        self.assertEqual((a.meta["gate_days"], a.meta["pass_at"], a.meta["minutes"]), (14, 16, 60))
        parts = a.meta["gate_parts"]
        self.assertEqual([p.get("optional", False) for p in parts], [False, True, False])   # 只有第二部分（自評）不擋升級
        self.assertEqual(sorted(a.meta["answer_files"]), sorted(EXAM_FILES))
        self.assertIn("1-27", grader.available_lessons(COURSE))
        self.assertNotIn("1-27B", grader.available_lessons(COURSE))

    def test_reference_answers_pass_the_whole_exam_a_and_b(self):
        for lid in ("1-27", "1-27B"):
            fresh_start(lid)
            all_right(lid)
            les = grader.load_lesson(lid, COURSE)
            exam = [c for c in les.checks if not c.get("gate_part")]
            out = grader.evaluate(les, L, only=exam)
            self.assertEqual(out.total, 20, lid)
            self.assertTrue(all(r.ok for r in out.results), (lid, [(r.id, r.detail) for r in out.results if not r.ok]))
            stages = [r.stage for r in out.results]
            self.assertEqual((stages.count("讀程式"), stages.count("手寫 v1.0")), (14, 6), lid)   # 70／30
            ids = sorted(r.id for r in out.results)
            if lid == "1-27":
                ids_a = ids
            else:
                self.assertEqual(ids, ids_a)   # 卷 B 的題目 id 跟卷 A 一樣（矯正包對照表共用）

    def test_start_files_do_not_pass(self):
        out = ev("1-27", [c["id"] for c in grader.load_lesson("1-27", COURSE).checks if not c.get("gate_part")])
        self.assertEqual(out.passed, 0, [(r.id, r.detail) for r in out.results if r.ok])

    def test_trace_answers_are_what_python_prints(self):
        """trace.txt 每一段的程式真的跑一次（拿掉行號），每一題的答案就是那一行印出的字。"""
        for lid, folder, right in (("1-27", D, RIGHT_A), ("1-27B", D / "B", RIGHT_B)):
            src = (folder / "start/trace.txt").read_text(encoding="utf-8")
            segs = re.findall(r"第.段：\n((?:\s*\d+(?:  .*)?\n)+)", src)
            self.assertEqual(len(segs), 3, lid)
            got = []
            for seg in segs:
                code = "\n".join(re.sub(r"^\s*\d+(  )?", "", ln) for ln in seg.rstrip("\n").split("\n"))
                p = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=30)
                self.assertEqual(p.returncode, 0, p.stderr)
                got += p.stdout.splitlines()
            self.assertEqual(got, right["trace"], lid)
            key = json.loads((folder / "answers/trace.json").read_text(encoding="utf-8"))
            self.assertEqual([q["accept"][0] for q in key["questions"]], right["trace"])

    def test_trace_spacing_and_plain_one_letter(self):
        answer("1-27", "trace.txt", ["35080", "2 0", "2電影", "電影 15", "跳過八十", "2 155"])
        answer("1-27", "plain.txt", ["C 或 B", "b", "A"])
        out = oks(ev("1-27", ["trace", "plain"]))
        self.assertEqual([out[f"trace-t{i}"] for i in range(1, 7)], [False, True, False, True, False, True])   # 中間的空白要一樣（keep_spaces）
        self.assertEqual([out[f"plain-p{i}"] for i in range(1, 4)], [False, True, True])   # 只能選一個（strict_choice）；小寫也認得

    def test_fix_three_bugs_are_independent(self):
        """三個 bug 隨便改好幾個，就是那幾題過、其他的不過（每一題只看一個 bug）。"""
        start = text("start/fix.py")
        edits = {"fix-month": ("        if month in e.date:", '        if e.date[:2] == month:'),
                 "fix-again": ("def month_of(entries, month, picked=[]):\n    \"\"\"交回 month 這個月（例如 \"11\"）的那幾筆，照原本的順序。\"\"\"\n",
                               "def month_of(entries, month, picked=None):\n    \"\"\"交回 month 這個月（例如 \"11\"）的那幾筆，照原本的順序。\"\"\"\n    if picked is None:\n        picked = []\n"),
                 "fix-big": ("if e.amount < best.amount:", "if e.amount > best.amount:")}
        for n in range(4):
            for combo in itertools.combinations(edits, n):
                src = start
                for k in combo:
                    self.assertIn(edits[k][0], src)
                    src = src.replace(*edits[k])
                write(L / "lessons/1-27/fix.py", src)
                out = oks(ev("1-27", list(edits)))
                self.assertEqual({k: out[k] for k in edits}, {k: k in combo for k in edits}, combo)

    def test_parsons_return_inside_for_is_wrong_output(self):
        ref = text("reference/parsons.py")
        write(L / "lessons/1-27/parsons.py", ref)
        self.assertEqual(oks(ev("1-27", ["pz"])), {"pz-order": True, "pz-run": True})
        write(L / "lessons/1-27/parsons.py", ref.replace("\n    return total, bad", "\n        return total, bad"))
        out = ev("1-27", ["pz"])
        self.assertEqual(oks(out), {"pz-order": True, "pz-run": False})
        self.assertIn("合計 120 元，看不懂 0 筆", next(r for r in out.results if r.id == "pz-run").detail)

    def test_ledger_v1_common_mistakes(self):
        ref = text("reference/ledger_v1.py")
        v1 = [c["id"] for c in grader.load_lesson("1-27", COURSE).checks if c["id"].startswith("v1-")]
        cases = {
            "接住 int 的錯、交回 0": (('    amount = int(text.replace(",", "").replace("元", ""))\n',
                                    '    try:\n        amount = int(text.replace(",", "").replace("元", ""))\n    except ValueError:\n        return 0\n'), {"v1-yuan-bad", "v1-run"}),
            "只擋負數（0 也收）": (("    if amount <= 0:", "    if amount < 0:"), {"v1-yuan-bad"}),
            "save 用 a": (('    with open(path, "w", encoding="utf-8") as f:', '    with open(path, "a", encoding="utf-8") as f:'), {"v1-save"}),
            "沒換行": (('f.write(f"{e.date},{e.item},{e.category},{e.amount}\\n")', 'f.write(f"{e.date},{e.item},{e.category},{e.amount}")'), {"v1-save", "v1-run"}),
            "檔案不存在沒處理": (("    if not path.exists():\n        return []\n", ""), {"v1-load", "v1-run"}),
            "金額沒變成整數": (("Entry(date, item, category, int(amount))", "Entry(date, item, category, amount)"), {"v1-load"}),
            "totals 只放最後一筆": (("out[e.category] = out.get(e.category, 0) + e.amount", "out[e.category] = e.amount"), {"v1-totals"}),
        }
        for name, ((a, b), bad) in cases.items():
            self.assertIn(a, ref, name)
            write(L / "lessons/1-27/ledger_v1.py", ref.replace(a, b))
            out = oks(ev("1-27", v1))
            self.assertEqual({k for k, v in out.items() if not v}, bad, name)

    def test_v1_checks_do_not_touch_the_ledger(self):
        write(L / "lessons/1-27/ledger_v1.py", text("reference/ledger_v1.py"))
        mine = write(L / "lessons/1-27/ledger_v1.txt", "11/01,早餐,早餐,60\n")
        before = snapshot(L / "lessons/1-27")
        out = ev("1-27", ["v1-load", "v1-save", "v1-run"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results if not r.ok])
        self.assertEqual(snapshot(L / "lessons/1-27"), before)
        self.assertEqual(mine.read_text(encoding="utf-8"), "11/01,早餐,早餐,60\n")

    def test_explain_form_is_self_check(self):
        p = L / "lessons/1-27/explain.md"
        self.assertFalse(ev("1-27", ["explain"]).results[0].ok)
        fill_explain(p, skip="為什麼這樣寫：")
        r = ev("1-27", ["explain"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("為什麼這樣寫：", r.detail)
        shutil.copy(D / "start_later/explain.md", p)
        fill_explain(p)
        self.assertTrue(ev("1-27", ["explain"]).results[0].ok)

    def test_budget_docstring_needs_four_labels_and_a_call(self):
        p = L / "lessons/1-27/budget.py"
        self.assertFalse(ev("1-27", ["budget-doc"]).results[0].ok)
        fill_doc(p, DOC.replace('set_budget(b, "2026-11", "8,000元") 交回 8000', "設定 11 月 8000 元"))
        r = ev("1-27", ["budget-doc"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("例子", r.detail)
        shutil.copy(D / "start_later/budget.py", p)
        fill_doc(p)
        self.assertTrue(ev("1-27", ["budget-doc"]).results[0].ok)

    def test_budget_asserts_catch_the_three_broken_versions(self):
        work = L / "lessons/1-27/checks_budget.py"
        out = ev("1-27", ["r3"])
        self.assertFalse(all(r.ok for r in out.results))
        write(work, text("answers/checks_budget.py"))
        out = ev("1-27", ["r3"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results if not r.ok])
        # 果凍兔式的檢查：只看交回的金額、只試寫得對的 → 0 元和 13 月溜過去
        write(work, "from budget_ai import set_budget\n\nb = {}\nassert set_budget(b, \"2026-11\", \"8,000元\") == 8000\n"
                    "assert b == {\"2026-11\": 8000}\nassert set_budget(b, \"2026-11\", \"6000\") == 6000\n"
                    "assert set_budget(b, \"2026-12\", \"1\") == 1\nassert b == {\"2026-11\": 6000, \"2026-12\": 1}\n")
        res = {r.id: r.ok for r in ev("1-27", ["r3"]).results}
        self.assertEqual({k: v for k, v in res.items() if re.search(r"-m\d$", k)}, {"r3-m1": False, "r3-m2": False, "r3-m3": True})
        # 學員拿到的 budget_ai.py 就是壞版本 2（AI 交回來的版本）
        self.assertEqual(text("start_later/budget_ai.py").split("\n", 2)[2], text("mutants/budget_ai_m2.py").split("\n", 1)[1])

    def test_remedial_key_matches_every_exam_check(self):
        rem = json.loads(text("remedial.json"))
        for lid in ("1-27", "1-27B"):
            les = grader.load_lesson(lid, COURSE)
            exam = [c for c in les.checks if not c.get("gate_part")]
            ids = sorted(r.id for r in grader.plan(les, L) if any(r.id == c["id"] or r.id.startswith(c["id"] + "-") for c in exam))
            self.assertEqual(sorted(rem["items"]), ids, lid)
        for t in rem["topics"].values():
            self.assertTrue((D / "practice" / t["practice"]).is_file(), t["practice"])
            self.assertTrue(all(w["lesson"] in {"1-5", "1-11", "1-15", "1-16", "1-17", "1-19", "1-20", "1-22", "1-23", "1-24"} for w in t["where"]))

    def test_practice_files_run_and_point_at_this_lesson(self):
        for p in sorted((D / "practice").glob("*.py")):
            body = p.read_text(encoding="utf-8")
            self.assertIn("lessons/1-27/practice/", body, p.name)
            self.assertNotIn("1-C3", body)
            self.assertNotIn("1-C4", body)
            if p.name == "p_indent.py":   # 拼圖練習：故意沒排好
                continue
            r = subprocess.run([sys.executable, "-I", str(p)], capture_output=True, text=True, timeout=30, cwd=str(WS))
            if p.name in ("p_class.py",):   # 要學員自己寫 Entry
                self.assertIn("NameError", r.stderr)
                continue
            self.assertEqual(r.returncode, 0, (p.name, r.stderr))
        for name in ("p_a.txt", "p_b.txt", "p_c.txt", "p_open.txt"):   # p_readfile.py、p_open.py 在自己旁邊寫的練習檔，測試完拿掉（不留在課程資料夾）
            (D / "practice" / name).unlink(missing_ok=True)
        self.assertEqual(sorted(x.suffix for x in (D / "practice").iterdir()), [".py"] * len(list((D / "practice").iterdir())))


class Flow(unittest.TestCase):
    """check.py：start、交卷（過了也寫矯正包）、第二三部分、第二部分不擋升級、滿 14 天升級、卷 B。"""

    @classmethod
    def setUpClass(cls):
        cls.home = fresh_dir("l127_home")

    def setUp(self):
        for lid in ("1-27", "1-27B"):
            d = L / "lessons" / lid
            if d.exists():
                shutil.rmtree(d)
        if (L / ".check").exists():
            shutil.rmtree(L / ".check")
        r = run_check(["setup", str(L)], make_env(self.home))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def run_(self, args, now):
        return run_check(args, make_env(self.home, now=now))

    def seed_days(self, n: int) -> None:
        lines = [json.dumps({"time": f"2026-10-{d:02d}T20:00:00+08:00", "lesson": "1-26", "predicted": None, "passed": 3, "total": 3, "failed": []})
                 for d in range(1, n + 1)]
        p = L / ".check/attempts.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        old = p.read_text(encoding="utf-8") if p.exists() else ""
        p.write_text("\n".join(lines) + "\n" + old, encoding="utf-8")

    def assert_screen(self, out: str) -> None:
        lines = out.splitlines()
        self.assertLessEqual(len(lines), 15, out)   # 影片錄的是這一段：一個畫面 17 列（指令＋15 行＋提示字元）
        for line in lines:
            self.assertLessEqual(cells(line), 70, line)

    def test_start_copies_only_the_exam(self):
        r = self.run_(["start", "1-27", "--predict", "18"], DAY1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(sorted(p.name for p in (L / "lessons/1-27").iterdir()), sorted(EXAM_FILES))
        self.assertIn("記下來了：開始前你猜會過 18／20 題。", r.stdout)
        self.assertIn("作答檔：lessons/1-27/（五個檔，ledger_v1.py 是手寫）", r.stdout)
        self.assert_screen(r.stdout)

    def test_bear_passes_a_then_part_two_is_optional_and_levels_up_after_14_days(self):
        self.run_(["start", "1-27", "--predict", "18"], DAY1)
        work = L / "lessons/1-27"
        all_right("1-27")
        answer("1-27", "trace.txt", BEAR_TRACE)
        write(work / "fix.py", bear_fix(text("start/fix.py")))
        write(work / "ledger_v1.py", bear_ledger(text("reference/ledger_v1.py")))
        t = datetime.fromisoformat("2026-11-20T18:55:00+08:00").timestamp()
        for f in EXAM_FILES:
            os.utime(work / f, (t, t))
        r = self.run_(["1-27", "--predict", "19", "--no-review"], "2026-11-20T18:56:00+08:00")
        out = r.stdout
        self.assertIn("結果：過了 17／20 題（16 題以上算過）", out)
        self.assertIn("  ✗ 讀程式  12／14", out)
        self.assertIn("  ✗ 手寫 v1.0  5／6", out)
        self.assertIn("大約 55 分鐘（參考 60 分鐘，只記錄）", out)
        self.assertIn("你猜 19 題，實際過了 17 題：高估了 2 題", out)
        self.assertIn("✓ 過了！第一部分通過。", out)
        self.assertIn("錯的那 3 題，矯正包一樣寫好了：帳本的 lessons/1-27/矯正包.md", out)
        self.assertIn("第二、三部分的檔案放進帳本了：", out)
        for f in ("budget.py", "budget_ai.py", "checks_budget.py", "explain.md"):
            self.assertTrue((work / f).is_file(), f)
        self.assert_screen(out)
        pack = (work / "矯正包.md").read_text(encoding="utf-8")
        for topic in ("sorted 的 key", "預設值 []", "整個重寫"):
            self.assertIn(topic, pack)
        # 第三部分做完、第二部分沒寫：天數不夠
        fill_doc(work / "budget.py")
        write(work / "checks_budget.py", text("answers/checks_budget.py"))
        r = self.run_(["1-27", "--no-review"], "2026-11-21T19:00:00+08:00")
        out = r.stdout
        self.assertIn("第一部分：11/20 卷 A 交卷就過了（17／20）。", out)
        self.assertIn("第二部分 v1.0 講解：✗ 還沒寫（自評，不擋升級）", out)
        self.assertRegex(out, r"第三部分 每月預算設定：✓ \d+／\d+")
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out)
        self.assertIn("第一、三部分都過了！練習天數 2／14 天，再練 12 天就升級", out)
        # 練習滿 14 天：第二部分還是沒寫，照樣升級
        self.seed_days(12)
        write(work / "fix.py", text("reference/fix.py"))
        write(work / "ledger_v1.py", text("reference/ledger_v1.py"))
        answer("1-27", "trace.txt", RIGHT_A["trace"])
        r = self.run_(["1-27", "--no-review"], "2026-11-22T19:00:00+08:00")
        out = r.stdout
        self.assertIn("卷 A 訂正：這次過了 20／20 題，全部都對！", out)
        self.assertIn("★ Lv1 下 看得懂（下）過關！第一、三部分過了，練習 15 天，可以升級了。", out)
        self.assert_screen(out)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertIn("level_up", prog["lessons"]["1-27"])
        self.assertNotIn("第二部分", prog["lessons"]["1-27"]["gate"])
        # 之後補寫第二部分：記下來
        fill_explain(work / "explain.md")
        r = self.run_(["1-27", "--no-review"], "2026-11-23T19:00:00+08:00")
        self.assertIn("第二部分 v1.0 講解：✓ 交了（自評，內容 check 不改對錯）", r.stdout)
        self.assertIn("（Lv1 下 看得懂（下）在 11/22 就過關了。）", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertIn("第二部分", prog["lessons"]["1-27"]["gate"])
        st = self.run_(["status"], "2026-11-23T19:05:00+08:00")
        self.assertIn("已升級", st.stdout)

    def test_fail_a_then_paper_b_next_day(self):
        self.run_(["start", "1-27", "--predict", "16"], DAY1)
        answer("1-27", "trace.txt", RIGHT_A["trace"])
        answer("1-27", "plain.txt", ["A", "A", "A"])   # 白話錯兩題、fix.py 和 ledger_v1.py 都沒動 → 沒過
        r = self.run_(["1-27", "--predict", "8", "--no-review", "--submit"], "2026-11-20T18:50:00+08:00")
        self.assertIn("這次沒過。矯正包在帳本的 lessons/1-27/矯正包.md：", r.stdout)
        self.assertIn("練完，明天以後考卷 B：uv run check.py start 1-27B", r.stdout)
        self.assert_screen(r.stdout)
        r = self.run_(["start", "1-27B", "--predict", "17"], "2026-11-20T19:00:00+08:00")
        self.assertIn("要隔天以後才能考", r.stdout)
        r = self.run_(["start", "1-27B", "--predict", "17"], "2026-11-21T18:00:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(sorted(p.name for p in (L / "lessons/1-27B").iterdir()), sorted(EXAM_FILES))
        all_right("1-27B")
        r = self.run_(["1-27B", "--predict", "18", "--no-review"], "2026-11-21T18:55:00+08:00")
        self.assertIn("結果：過了 20／20 題（16 題以上算過）", r.stdout)
        self.assertIn("✓ 過了！第一部分通過。", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-27"]["passed_via"], "B")


if __name__ == "__main__":
    unittest.main()
