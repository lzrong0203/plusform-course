"""1-25〈Debugger 與編輯器導覽〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 加的東西（只對寫了它的題目生效）：filled 的 md_list（bug 回報的「## 重現步驟」底下至少一行 Markdown 編號步驟）。
第①圈 debug.txt 4 題（debugger 與編輯器導覽，對答）；第②圈 tutor.md（filled）、ask.txt 3 題；
第③圈 bug_report.md（filled 三段＋md_list）、report.py 改用課程的修正版 dates_fixed.py（run＋ast_require imports）、
checks_dates.py（chaff assert：學員的重現步驟在修正版上全部成立＝修正版測試全綠，抓 3 個 AI 修錯的版本：
m1 那個月沒有這一天就跳到再下一個月的 1 號、m2 一律換成下個月的最後一天、m3 沒處理 12 月）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l125"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-25"
D = COURSE / "lessons" / LID
# Python 3.13（帳本釘的版本）印前一種；3.14 起改成後一種（run_all 可能用 3.14 跑）
VALUE_ERR = re.compile(r"ValueError: day (is out of range for month|31 must be in range 1\.\.28 for month 2 in year 2026)$")
CK_HEAD = "from datetime import date\n\nfrom dates_fixed import next_month\n\n"
REPRO = "assert next_month(date(2026, 1, 31)) == date(2026, 2, 28)\n"    # 回報裡的那一天
OLD_OK = "assert next_month(date(2026, 1, 15)) == date(2026, 2, 15)\n"   # 原本就好好的日子
YEAR_END = "assert next_month(date(2026, 12, 15)) == date(2027, 1, 15)\n"  # 年底
BEAR = CK_HEAD + REPRO + OLD_OK + YEAR_END   # 影片裡熊寫的三條
GOOD_REPORT = """# 月報：扣款日是 1 月 31 日時，算下期扣款就當掉

## 重現步驟
1. 在帳本資料夾打 `uv run lessons/1-25/report.py`
2. 看終端機印出來的字

## 預期
印出 下期扣款 2026-02-28（2 月沒有 31 號，用 2 月最後一天）

## 實際
印出 這期扣款 2026-01-31 以後就當掉：
```
ValueError: day is out of range for month
```
"""


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def mine(name: str) -> Path:
    return L / "lessons" / LID / name


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
    return next(r for r in out.results if r.id == suffix or (r.id.startswith("r3") and r.id.rsplit("-", 1)[-1] == suffix))


def r3(text: str) -> grader.Outcome:
    write(mine("checks_dates.py"), text)
    return ev(["r3"])


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def run_start(files: dict[str, str] | None = None, script: str = "report.py") -> subprocess.CompletedProcess:
    """把起點檔複製到暫存資料夾（可以換掉幾個檔）跑一次。"""
    t = Path(tempfile.mkdtemp(prefix="c125-"))
    for f in (D / "start").glob("*.py"):
        shutil.copyfile(f, t / f.name)
    for name, text in (files or {}).items():
        (t / name).write_text(text, encoding="utf-8")
    try:
        return subprocess.run([sys.executable, "-B", script], cwd=t, capture_output=True, text=True)
    finally:
        shutil.rmtree(t, ignore_errors=True)


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Program(unittest.TestCase):
    """起點的月報程式：影片和作業的事實都從這裡來。"""

    def test_start_crashes_like_the_video(self):
        p = run_start()
        self.assertEqual(p.stdout, "這期扣款 2026-01-31\n")
        self.assertRegex(p.stderr.rstrip(), VALUE_ERR)
        self.assertIn('dates.py", line 3, in next_month', p.stderr)
        self.assertIn('report.py", line 9, in <module>', p.stderr)

    def test_fixed_import_prints_expected(self):
        rep = (D / "start" / "report.py").read_text(encoding="utf-8").replace("from dates import", "from dates_fixed import")
        p = run_start({"report.py": rep})
        self.assertEqual((p.stdout, p.stderr), ("這期扣款 2026-01-31\n下期扣款 2026-02-28\n", ""))

    def test_debug_questions_line_numbers(self):
        """debug.txt 寫的行號照起點檔：report.py 第 7 行讀 PAY_DAY、第 9 行呼叫 next_month；settings.py 第 2 行定出 15；card.py 第 5 行改成 31。"""
        rep = (D / "start" / "report.py").read_text(encoding="utf-8").splitlines()
        self.assertEqual(rep[6], "d = date(2026, 1, settings.PAY_DAY)")
        self.assertIn("next_month(d)", rep[8])
        self.assertEqual((D / "start" / "settings.py").read_text(encoding="utf-8").splitlines()[1], "PAY_DAY = 15")
        card = (D / "start" / "card.py").read_text(encoding="utf-8").splitlines()
        self.assertTrue(card[4].strip().startswith("settings.PAY_DAY = 31"), card)
        writes = {}
        for f in (D / "start").glob("*.py"):
            for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
                if isinstance(n, ast.Assign):
                    for tg in n.targets:
                        nm = tg.attr if isinstance(tg, ast.Attribute) else getattr(tg, "id", None)
                        if nm == "PAY_DAY":
                            writes.setdefault(f.name, []).append(n.lineno)
        self.assertEqual(writes, {"settings.py": [2], "card.py": [5]})

    def test_replace_fact(self):
        """ask.txt 第 2 題：replace 只換月份，想做出 2 月 31 日 → ValueError 原文。"""
        p = subprocess.run([sys.executable, "-B", "-c", "from datetime import date\ndate(2026, 1, 31).replace(month=2)"],
                           capture_output=True, text=True)
        self.assertRegex(p.stderr.rstrip(), VALUE_ERR)

    def test_fixed_version_dates(self):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); from datetime import date; from dates_fixed import next_month as n\n"
                "for d in [date(2026,1,31), date(2026,1,15), date(2026,12,15), date(2026,12,31), date(2028,1,31), date(2026,3,31)]: print(n(d))")
        p = subprocess.run([sys.executable, "-B", "-c", code, str(D / "start")], capture_output=True, text=True)
        self.assertEqual(p.stdout.split(), ["2026-02-28", "2026-02-15", "2027-01-15", "2027-01-31", "2028-02-29", "2026-04-30"], p.stderr)

    def test_start_equals_reference(self):
        """課程的修正版：起點檔和正確版一樣（正確版第一行是老師的說明）。"""
        for name in ("dates_fixed.py", "settings.py", "card.py"):
            refl = (D / "reference" / name).read_text(encoding="utf-8").splitlines(keepends=True)[1:]
            self.assertEqual("".join(refl), (D / "start" / name).read_text(encoding="utf-8"), name)


class Debug(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("debug.txt", ["B", "A", "C", "B"])
        out = ev(["debug"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_common_mistakes(self):
        """以為亮起來的那一行跑完了、呼叫堆疊最上面是 report.py、F12 跳到改它的地方、改它的是 settings.py。"""
        answer("debug.txt", ["A", "B", "A", "A"])
        out = ev(["debug"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_key(self):
        key = json.loads((D / "answers" / "debug.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"] for q in key["questions"]], [["B"], ["A"], ["C"], ["B"]])


class Ask(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("ask.txt", ["B", "C", "A"])
        out = ev(["ask"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_wrong_answers(self):
        answer("ask.txt", ["A", "A", "C"])
        out = ev(["ask"])
        self.assertFalse(any(r.ok for r in out.results))


class Tutor(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_then_filled(self):
        out = ev(["tutor"])
        self.assertFalse(out.results[0].ok)
        p = mine("tutor.md")
        txt = p.read_text(encoding="utf-8")
        for lab in ("我指的那一行：", "家教怎麼說：", "我用 debugger 看到的："):
            txt = txt.replace(lab + "\n", lab + "寫了一些字\n", 1)
        p.write_text(txt, encoding="utf-8")
        out = ev(["tutor"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)


class BugReport(unittest.TestCase):
    def setUp(self):
        start()

    def test_template_not_done(self):
        out = ev(["bug-report"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("重現步驟", out.results[0].detail)

    def test_good_report(self):
        write(mine("bug_report.md"), GOOD_REPORT)
        out = ev(["bug-report"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_good_report_with_checklist(self):
        """寫在起點檔裡（最下面的自評表留著、打了 x）：自評表不算進「實際」，照樣過。"""
        tail = (D / "start" / "bug_report.md").read_text(encoding="utf-8").split("## 自評")[1]
        write(mine("bug_report.md"), GOOD_REPORT + "\n## 自評" + tail.replace("- [ ]", "- [x]"))
        out = ev(["bug-report"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_steps_must_be_numbered(self):
        """重現步驟寫成一段話（沒有 1. 2.）：md_list 擋下來，說要寫成編號步驟。"""
        write(mine("bug_report.md"), GOOD_REPORT.replace("1. 在帳本資料夾打", "在帳本資料夾打").replace("2. 看終端機", "然後看終端機"))
        out = ev(["bug-report"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("編號", out.results[0].detail)

    def test_empty_number_is_not_a_step(self):
        """只留起點檔的「1. 」沒寫字：算還空着。"""
        write(mine("bug_report.md"), GOOD_REPORT.replace("1. 在帳本資料夾打 `uv run lessons/1-25/report.py`\n2. 看終端機印出來的字\n", "1. \n"))
        out = ev(["bug-report"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("還空着", out.results[0].detail)

    def test_missing_expected(self):
        write(mine("bug_report.md"), GOOD_REPORT.replace("印出 下期扣款 2026-02-28（2 月沒有 31 號，用 2 月最後一天）\n", ""))
        out = ev(["bug-report"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("## 預期", out.results[0].detail)

    def test_md_list_only_where_written(self):
        """md_list 只對寫了它的題目生效：別課的 filled（1-23 tutor.md）一段話照樣過。"""
        spec = {"type": "filled", "id": "x", "file": "lessons/1-25/x.md", "labels": ["A："], "count": 1}
        write(mine("x.md"), "A：只寫一段話，沒有編號\n")
        les = grader.load_lesson(LID, COURSE)
        out = grader.evaluate(les, L, only=[spec])
        self.assertTrue(out.results[0].ok, out.results[0].detail)
        mine("x.md").unlink()


class ReportFixed(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_fails(self):
        out = ev(["report-fixed"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("dates_fixed", out.results[0].detail)

    def test_reference_passes(self):
        p = mine("report.py")
        p.write_text(p.read_text(encoding="utf-8").replace("from dates import", "from dates_fixed import"), encoding="utf-8")
        out = ev(["report-fixed"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_removing_card_is_wrong(self):
        """把 use_card() 拿掉（不讓它改成 31）：沒當掉，可是印出 1 月 15 日，跟預期不一樣。"""
        p = mine("report.py")
        p.write_text(p.read_text(encoding="utf-8").replace("from dates import", "from dates_fixed import").replace("use_card()\n", ""),
                     encoding="utf-8")
        out = ev(["report-fixed"])
        self.assertFalse(out.results[0].ok)

    def test_fix_in_dates_without_import_change(self):
        """沒改第 4 行、自己把 dates.py 改成修正版：ast_require 要它從 dates_fixed 拿。"""
        write(mine("dates.py"), (D / "start" / "dates_fixed.py").read_text(encoding="utf-8"))
        out = ev(["report-fixed"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("from dates_fixed import next_month", out.results[0].detail)


class R3(unittest.TestCase):
    def setUp(self):
        start()

    def test_bear_checks_catch_all(self):
        out = r3(BEAR)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_each_check_catches(self):
        """重現步驟只抓 m1；原本好好的日子只抓 m2；m3 只有年底抓得到（年底那一條三個都抓得到：m1 跳到 14 月當掉、m2 變成 1 月 31 日）。"""
        def caught(body):
            out = r3(CK_HEAD + body)
            return [part(out, f"m{k}").ok for k in (1, 2, 3)]
        self.assertEqual(caught(REPRO), [True, False, False])
        self.assertEqual(caught(OLD_OK), [False, True, False])
        self.assertEqual(caught(YEAR_END), [True, True, True])

    def test_start_catches_none(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertEqual([part(out, f"m{k}").ok for k in (1, 2, 3)], [False, False, False])

    def test_wrong_expectation_fails_on_fixed(self):
        """預期寫成 3 月 3 日（以為會往後推）：在課程的修正版上不成立，修正版測試不是全綠。"""
        out = r3(CK_HEAD + "assert next_month(date(2026, 1, 31)) == date(2026, 3, 3)\n" + OLD_OK + YEAR_END)
        self.assertFalse(part(out, "wheat").ok)

    def test_bear_checks_on_fixed_print_nothing(self):
        """影片裡熊的三條，跑課程的修正版：什麼都沒印（VHS 實錄 t01 的樣子）。"""
        with tempfile.TemporaryDirectory() as t:
            shutil.copyfile(D / "start" / "dates_fixed.py", Path(t) / "dates_fixed.py")
            Path(t, "checks_dates.py").write_text(BEAR, encoding="utf-8")
            p = subprocess.run([sys.executable, "-B", "checks_dates.py"], cwd=t, capture_output=True, text=True)
            self.assertEqual((p.returncode, p.stdout, p.stderr), (0, "", ""))

    def test_ai_fix_in_video(self):
        """影片第③圈 AI 的修正版（m1）：照重現步驟跑，下期扣款印出 2026-03-01。"""
        rep = (D / "start" / "report.py").read_text(encoding="utf-8").replace("from dates import", "from dates_fixed import")
        p = run_start({"report.py": rep, "dates_fixed.py": (D / "mutants" / "dates_fixed_m1.py").read_text(encoding="utf-8")})
        self.assertEqual((p.stdout, p.stderr), ("這期扣款 2026-01-31\n下期扣款 2026-03-01\n", ""))


if __name__ == "__main__":
    unittest.main()
