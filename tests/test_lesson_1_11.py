"""1-11〈for、range、enumerate 與兩層迴圈〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

兩個新東西，都只對寫了它的 checks.json 生效：
  - 拼圖（type parsons，ParsonsCheck）：把打亂的五行排回去、自己縮排。order 題看「題目給的行一行不少、一行不多、沒有改字、
    縮排是四的倍數、Python 讀得懂」；run 題看排好跑出來跟範例一不一樣（排法不只一種也照結果判）。
  - 第③圈 chaff 的 table_facts 模式：學員先不跑程式，寫下預算表「應該有幾列」「第 3 天晚餐那格」，check 跑正確版和 3 個壞版本，
    數列、找那一格，一件一件比。壞版本：range(1, 7) 少一天（列數抓到）、total = 0 放進外層每天重算（只有那一格抓得到，主角）、
    print() 縮進內層每格各一列（列數抓到；那一格照標籤找，數字還是對的，所以藏得住）。
week.py 有 swap：check 把 week 換成別的七個數字再跑一次，把答案寫死的過不了。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l111"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-11"
D = COURSE / "lessons" / LID
HEAD = "# 1-11 第三圈：先別跑 plan.py。\n"
# 影片裡熊的第一版：只寫了列數 → 壞版本 2（每天重算）溜過去；第二版補上第 3 天晚餐 990 → 三個全抓到
BEAR_ROWS = HEAD + "應該有幾列：7\n第 3 天晚餐那格：？\n"
BEAR_BOTH = HEAD + "應該有幾列：7\n第 3 天晚餐那格：990\n"
PZ_OK = (D / "reference" / "parsons.py").read_text(encoding="utf-8")


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
    return next(r for r in out.results if r.id.rsplit("-", 1)[-1] == suffix)


def r3(text: str) -> grader.Outcome:
    write(L / "lessons" / LID / "facts.txt", text)
    return ev(["r3"])


def pz(text: str) -> grader.Outcome:
    write(L / "lessons" / LID / "parsons.py", text)
    return ev(["pz"])


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


class TableFacts(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_facts_catch_all_three(self):
        out = r3((D / "answers" / "facts.txt").read_text(encoding="utf-8"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 2 行抓到")   # 6 列（老師的 facts.txt 第 1 行是 # 說明）
        self.assertEqual(part(out, "m2").note, "被第 3 行抓到")   # 第 3 天晚餐 330
        self.assertEqual(part(out, "m3").note, "被第 2 行抓到")   # 21 列
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_bear_rows_only_lets_the_daily_reset_slip(self):
        out = r3(BEAR_ROWS)
        self.assertTrue(part(out, "count").ok and part(out, "wheat").ok, [(r.id, r.detail) for r in out.results])
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, False, True])
        self.assertIn("每一天都從 0 重新算", part(out, "m2").detail)
        self.assertIn("你的檢查抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)

    def test_bear_both_facts_catch_all(self):
        out = r3(BEAR_BOTH)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_cell_only_misses_the_short_and_split_tables(self):
        out = r3(HEAD + "應該有幾列：？\n第 3 天晚餐那格：990\n")
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [False, True, False])

    def test_wrong_cell_value_fails_on_reference_without_revealing_it(self):
        for wrong in ("330", "150"):
            out = r3(HEAD + f"應該有幾列：7\n第 3 天晚餐那格：{wrong}\n")
            r = part(out, "wheat")
            self.assertFalse(r.ok, wrong)
            self.assertIn(f"第 3 天晚餐那格：{wrong}", r.detail)
            self.assertIn("到第 3 天晚餐是幾天加起來", r.detail)
            self.assertNotIn("990", r.detail)

    def test_wrong_row_count_hint(self):
        out = r3(HEAD + "應該有幾列：8\n第 3 天晚餐那格：？\n")
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("一週有幾天", part(out, "wheat").detail)

    def test_start_file_is_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你寫了 0 件事，這課要至少 1 件（還有 2 行有「？」沒填完）", part(out, "count").detail)
        self.assertIn("還沒寫任何一件事", part(out, "wheat").detail)

    def test_changed_label_is_explained(self):
        out = r3(HEAD + "列數：7\n")
        self.assertIn("冒號前面的字被改到了", out.results[0].detail)
        self.assertIn("「應該有幾列」「第 3 天晚餐那格」", out.results[0].detail)

    def test_value_must_be_a_number(self):
        out = r3(HEAD + "應該有幾列：七\n")
        self.assertIn("冒號後面寫一個整數", out.results[0].detail)
        out = r3(HEAD + "應該有幾列：330×3\n")
        self.assertIn("冒號後面寫一個整數", out.results[0].detail)

    def test_units_spaces_halfwidth_colon_crlf_bom_are_fine(self):
        out = r3("﻿" + HEAD.replace("\n", "\r\n") + "應該有幾列: 7 列\r\n第3天晚餐那格 ： 990 元\r\n")
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_cell_is_found_by_label_not_by_line(self):
        rows = ["第 1 天：60", "180", "330", "第 2 天：390", "510", "660", "第 3 天：720", "840", "990", "第 4 天：1050"]
        fact = {"kind": "cell", "row": "第 3 天", "col": 3}
        self.assertEqual(grader.ChaffCheck.fact_value(fact, rows), 990)
        self.assertEqual(grader.ChaffCheck.fact_value(fact, ["第 13 天：1 2 3", "第 3 天：4 5 6"]), 6)   # 第 13 天不是第 3 天
        self.assertIsNone(grader.ChaffCheck.fact_value(fact, ["第 3 天：4 5"]))
        self.assertIsNone(grader.ChaffCheck.fact_value(fact, ["第 1 天：60 180 330"]))

    def test_other_chaff_modes_untouched(self):
        les = grader.load_lesson("1-1", COURSE)
        self.assertEqual(next(c for c in les.checks if c["type"] == "chaff")["mode"], "expected_text")


class Parsons(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_file_fails_order_with_indentation_hint(self):
        out = ev(["pz"])
        self.assertEqual([r.ok for r in out.results], [False, False])
        self.assertIn("縮排不對", part(out, "order").detail)
        self.assertIn("下一行要往右縮四格", part(out, "order").detail)
        self.assertIn("先把上一題", part(out, "run").detail)

    def test_reference_order_passes(self):
        out = pz(PZ_OK)
        self.assertEqual([r.ok for r in out.results], [True, True], [r.detail for r in out.results])

    def test_eight_space_indent_and_kept_comments_are_fine(self):
        alt = "# 我排好的\n" + PZ_OK.replace("\n    for cost", "\n        for cost").replace("\n        n = n + 1", "\n            n = n + 1") \
            .replace("\n        print(", "\n            print(")
        out = pz(alt)
        self.assertEqual([r.ok for r in out.results], [True, True], [r.detail for r in out.results])

    def test_counter_inside_outer_loop_restarts(self):
        bad = 'for day in range(1, 4):\n    n = 0\n    for cost in [60, 120, 150]:\n        n = n + 1\n        print("第", n, "餐：第", day, "天，預算", cost, "元")\n'
        out = pz(bad)
        self.assertEqual([r.ok for r in out.results], [True, False])
        self.assertIn("跟範例不一樣", part(out, "run").detail)
        self.assertIn("n = 0 只做一次", part(out, "run").detail)

    def test_print_before_adding_starts_at_zero(self):
        bad = 'n = 0\nfor day in range(1, 4):\n    for cost in [60, 120, 150]:\n        print("第", n, "餐：第", day, "天，預算", cost, "元")\n        n = n + 1\n'
        out = pz(bad)
        self.assertEqual([r.ok for r in out.results], [True, False])
        self.assertIn("第 0 餐", part(out, "run").detail)

    def test_changed_extra_or_missing_lines_are_named(self):
        out = pz(PZ_OK.replace("n = n + 1", "n += 1"))
        self.assertFalse(part(out, "order").ok)
        self.assertIn("「n += 1」不是拼圖裡的行", part(out, "order").detail)
        self.assertIn("一共有 2 個地方不對", part(out, "order").detail)   # 只先講第一個（少了的那一行排在後面）
        out = pz(PZ_OK.replace("        n = n + 1\n", ""))
        self.assertIn("少了「n = n + 1」這一行", part(out, "order").detail)
        out = pz(PZ_OK + 'print("完成")\n')
        self.assertIn("不是拼圖裡的行", part(out, "order").detail)

    def test_spacing_inside_a_line_is_not_a_change(self):
        out = pz(PZ_OK.replace("range(1, 4)", "range(1,4)"))
        self.assertEqual([r.ok for r in out.results], [True, True], [r.detail for r in out.results])

    def test_tab_and_odd_indent(self):
        out = pz(PZ_OK.replace("\n    for cost", "\n\tfor cost"))
        self.assertIn("Tab", part(out, "order").detail)
        out = pz(PZ_OK.replace("\n    for cost", "\n  for cost"))
        self.assertIn("往右縮了 2 格", part(out, "order").detail)

    def test_missing_file(self):
        (L / "lessons" / LID / "parsons.py").unlink()
        out = ev(["pz"])
        self.assertIn("uv run check.py start 1-11", out.results[0].detail)


class Programs(unittest.TestCase):
    def setUp(self):
        start()

    def test_references_pass_and_starts_do_not(self):
        ids = ["week-1", "week-2", "number", "table"]
        out = ev(ids)
        self.assertFalse(any(r.ok for r in out.results))
        for f in ("week.py", "number.py", "table.py"):
            shutil.copy(D / "reference" / f, L / "lessons" / LID / f)
        out = ev(ids)
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_hardcoded_week_fails_the_swap(self):
        write(L / "lessons" / LID / "week.py", 'week = [120, 85, 200, 95, 150, 60, 180]\nprint("一週一共 890 元")\nprint("超過預算 2 天")\nprint("最多的一天 200 元")\n')
        out = ev(["week-1", "week-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])
        self.assertIn("換成 [100, 160, 90, 300, 150, 151, 20]", out.results[1].detail)

    def test_rabbit_total_inside_the_loop(self):
        src = (D / "reference" / "week.py").read_text(encoding="utf-8")
        bad = src.replace("total = 0\n", "").replace("for cost in week:\n", "for cost in week:\n    total = 0\n")
        write(L / "lessons" / LID / "week.py", bad)
        out = ev(["week-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("一週一共 180 元", out.results[0].detail)
        self.assertIn("放在迴圈外面", out.results[0].detail)

    def test_over_budget_counts_strictly_greater(self):
        src = (D / "reference" / "week.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "week.py", src.replace("cost > 150", "cost >= 150"))
        out = ev(["week-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("超過預算 3 天", out.results[0].detail)

    def test_enumerate_without_start_begins_at_zero(self):
        src = (D / "reference" / "number.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "number.py", src.replace(", start=1", ""))
        out = ev(["number"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("第 0 天 120 元", out.results[0].detail)

    def test_newline_inside_inner_loop_breaks_the_table(self):
        src = (D / "reference" / "table.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "table.py", src.replace("\n    print()\n", "\n        print()\n"))
        out = ev(["table"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("縮進內層", out.results[0].detail)

    def test_range_one_to_seven_misses_a_day(self):
        src = (D / "reference" / "table.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "table.py", src.replace("range(1, 8)", "range(1, 7)"))
        self.assertFalse(ev(["table"]).results[0].ok)


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_range_quiz(self):
        answer("range.txt", ["5", "7", "a", "6 次"])
        out = ev(["range"])
        self.assertEqual([r.ok for r in out.results], [True] * 4, [r.detail for r in out.results])
        answer("range.txt", ["4", "8", "B", "5"])
        out = ev(["range"])
        self.assertEqual([r.ok for r in out.results], [False] * 4)

    def test_trace_quiz(self):
        answer("trace_quiz.txt", ["4", "15", "10 行"])
        out = ev(["trace"])
        self.assertEqual([r.ok for r in out.results], [True] * 3, [r.detail for r in out.results])
        answer("trace_quiz.txt", ["3", "8", "16"])
        out = ev(["trace"])
        self.assertEqual([r.ok for r in out.results], [False] * 3)
        self.assertIn("一輪一輪", out.results[2].detail)


class FullRun(unittest.TestCase):
    def test_full_run_through_check_py(self):
        """check.py 1-11：全對 18 題；每行壓在 68 欄內（VHS 錄影 70 欄）。"""
        start()
        home = fresh_dir("l111_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_check(["start", "1-11"], env, stdin="")
        self.assertIn("uv run check.py 1-11", r.stdout)
        work = L / "lessons" / LID
        for f in ("week.py", "number.py", "table.py", "parsons.py"):
            shutil.copy(D / "reference" / f, work / f)
        write(work / "facts.txt", BEAR_BOTH)
        answer("range.txt", ["5", "7", "A", "6"])
        answer("trace_quiz.txt", ["4", "15", "10"])
        r = run_check(["1-11", "--predict", "18", "--no-review"], env)
        self.assertIn("18／18", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", r.stdout)
        for line in r.stdout.splitlines():
            self.assertLessEqual(sum(2 if ord(ch) > 0x2E7F else 1 for ch in line), 70, line)


if __name__ == "__main__":
    unittest.main()
