"""1-21〈模組與 import：別人寫好的工具，和 AI 編出來的套件〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

這一課第一次有兩個檔：main.py 用 from money import fmt, total 拿旁邊 money.py 的函式。
grader 加的東西（只對寫了它的題目生效）：run 的 expect_today（照跑的那一天算出來的一行，例如「本月 2026-11」）、swap 的 siblings（換掉一行再跑時，同一個資料夾的其他 .py 一起複製過去）、
ast_require 的 imports（from money import fmt, total，而且 main.py 裡不能再留一份 def）、calls（要呼叫 today、strptime，不能寫死）。
其他用到的是前幾課已有的：call（直接測 money.py 的 total、fmt；載入時 __name__ 是 "money"，if __name__ == "__main__": 下面那段不跑）、run（expect_exact、expect_contains、expect_not_contains）、answers（strict_choice）、filled。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import shutil
import unittest
from datetime import date
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l121"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-21"
D = COURSE / "lessons" / LID
REF_MONEY = (D / "reference" / "money.py").read_text(encoding="utf-8")
REF_MAIN = (D / "reference" / "main.py").read_text(encoding="utf-8")
MONEY_FUNCS = 'def total(amounts):\n    return sum(amounts)\n\n\ndef fmt(amount):\n    return f"{amount:,} 元"\n'
CHECKS3 = 'assert total([120, 85]) == 205\nassert fmt(1250) == "1,250 元"\nprint("money.py 自己的檢查都過了")\n'


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


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def oks(out: grader.Outcome) -> list[bool]:
    return [r.ok for r in out.results]


def details(out: grader.Outcome) -> list:
    return [(r.id, r.ok, r.detail) for r in out.results]


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Money(unittest.TestCase):
    IDS = ["total-1", "total-2", "fmt-1", "fmt-2", "money-self"]

    def setUp(self):
        start()

    def test_reference_passes(self):
        write(mine("money.py"), REF_MONEY)
        out = ev(self.IDS)
        self.assertTrue(all(oks(out)), details(out))

    def test_start_file_fails(self):
        """起點檔：函式還沒搬過來，載入就 NameError（最下面的檢查用到 total）。"""
        out = ev(self.IDS)
        self.assertFalse(any(oks(out)), details(out))

    def test_moved_but_not_guarded(self):
        """函式搬過來了、三行檢查還在最外層：直接呼叫 total、fmt 對，直接跑 money.py 也印得出來（這題只看自己跑）。"""
        write(mine("money.py"), MONEY_FUNCS + "\n\n" + CHECKS3)
        out = ev(self.IDS)
        self.assertTrue(all(oks(out)), details(out))

    def test_guard_block_not_run_by_call(self):
        """call 載入 money.py 時 __name__ 是 "money"：if __name__ == "__main__": 下面放一行會當掉的，也不影響直接呼叫。"""
        write(mine("money.py"), MONEY_FUNCS + '\n\nif __name__ == "__main__":\n    raise SystemExit("不該跑到這裡")\n')
        out = ev(["total-1", "fmt-1"])
        self.assertTrue(all(oks(out)), details(out))
        out = ev(["money-self"])
        self.assertFalse(out.results[0].ok)

    def test_fmt_without_comma(self):
        write(mine("money.py"), MONEY_FUNCS.replace("{amount:,}", "{amount}") + '\n\nif __name__ == "__main__":\n    print("money.py 自己的檢查都過了")\n')
        out = ev(["fmt-1", "fmt-2", "total-1"])
        got = {r.id: r for r in out.results}
        self.assertEqual([got[k].ok for k in ("fmt-1", "fmt-2", "total-1")], [False, False, True], details(out))
        self.assertIn("1,250 元", got["fmt-1"].detail)


class Main(unittest.TestCase):
    IDS = ["main-1", "main-2"]

    def setUp(self):
        start()
        write(mine("money.py"), REF_MONEY)

    def test_reference_passes(self):
        write(mine("main.py"), REF_MAIN)
        out = ev(self.IDS)
        self.assertTrue(all(oks(out)), details(out))

    def test_start_file_fails(self):
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok, details(out))

    def test_money_checks_leak_into_main(self):
        """money.py 的三行檢查還在最外層：import 的時候跟著跑，main.py 印出「money.py 自己的檢查都過了」→ 不過。"""
        write(mine("money.py"), MONEY_FUNCS + "\n\n" + CHECKS3)
        write(mine("main.py"), REF_MAIN)
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("不應該出現", out.results[0].detail)

    def test_copied_functions_instead_of_import(self):
        """把 total、fmt 留在 main.py（沒有 import）：印出來一樣，但 ast_require 的 imports 擋下來。"""
        src = REF_MAIN.replace("from money import fmt, total\n", "\n" + MONEY_FUNCS + "\n")
        write(mine("main.py"), src)
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("from money import fmt, total", out.results[0].detail)

    def test_import_and_keep_defs(self):
        """import 了、可是 main.py 裡還留一份 def：一樣不過（要剪下，不是複製）。"""
        src = REF_MAIN.replace("from money import fmt, total\n", "from money import fmt, total\n\n" + MONEY_FUNCS + "\n")
        write(mine("main.py"), src)
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok)

    def test_whole_module_import_ok(self):
        """import money、用 money.fmt(money.total(…)) 也算對。"""
        src = REF_MAIN.replace("from money import fmt, total\n", "import money\n").replace("fmt(total(amounts))", "money.fmt(money.total(amounts))")
        write(mine("main.py"), src)
        out = ev(self.IDS)
        self.assertTrue(all(oks(out)), details(out))

    def test_month_hardcoded(self):
        """本月寫死成某個月：沒有 date.today() → calls 擋下來。"""
        src = REF_MAIN.replace('date.today().strftime("%Y-%m")', '"2026-11"')
        write(mine("main.py"), src)
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("date.today()", out.results[0].detail)

    def test_wrong_month_format(self):
        """本月用 %Y/%m（斜線）：照今天算的那一行對不上 → 不過；說明裡有今天的年月。"""
        src = REF_MAIN.replace('"%Y-%m")', '"%Y/%m")')
        write(mine("main.py"), src)
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn(date.today().strftime("本月 %Y-%m"), out.results[0].detail)

    def test_capital_M(self):
        """月份寫成大寫 %M（分鐘）：strptime 照樣跑、印出 1 3 → 不過（找不到 11 3）。"""
        src = REF_MAIN.replace('"%Y-%m-%d"', '"%Y-%M-%d"')
        write(mine("main.py"), src)
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("11 3", out.results[0].detail)

    def test_printed_11_3_directly(self):
        """直接 print(11, 3)、沒有用 strptime：calls 擋下來。"""
        src = REF_MAIN.replace('d = datetime.strptime("2026-11-03", "%Y-%m-%d")\nprint(d.month, d.day)\n', "print(11, 3)\n")
        write(mine("main.py"), src)
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("strptime", out.results[0].detail)

    def test_total_hardcoded(self):
        """合計寫死成 1,820 元：換 amounts 再跑一次就抓到（swap 的 siblings 把 money.py 一起帶過去，才 import 得到）。"""
        src = REF_MAIN.replace('print("合計", fmt(total(amounts)))', 'print("合計", "1,820 元")\nfmt(total(amounts))')
        write(mine("main.py"), src)
        out = ev(self.IDS)
        self.assertEqual(oks(out), [True, False], details(out))
        self.assertIn("2,300 元", out.results[1].detail)

    def test_money_in_other_folder(self):
        """money.py 不在 main.py 旁邊：ModuleNotFoundError。"""
        write(mine("main.py"), REF_MAIN)
        mine("money.py").unlink()
        write(L / "lessons" / "money.py", REF_MONEY)
        out = ev(["main-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("ModuleNotFoundError", out.results[0].detail)
        (L / "lessons" / "money.py").unlink()


class AstRules(unittest.TestCase):
    """ast_require 的 imports、calls 本身（不跑程式）。"""

    def test_imports(self):
        rule = [dict(name="money", kind="imports", names=["fmt", "total"])]
        self.assertEqual(grader.ast_problems("from money import fmt, total\n", rule), [])
        self.assertEqual(grader.ast_problems("from money import total, fmt\n", rule), [])
        self.assertEqual(grader.ast_problems("import money\n", rule), [])
        self.assertEqual(len(grader.ast_problems("from money import fmt\n", rule)), 1)
        self.assertEqual(len(grader.ast_problems("from moneys import fmt, total\n", rule)), 1)
        self.assertEqual(len(grader.ast_problems("from money import fmt, total\ndef fmt(a):\n    return a\n", rule)), 1)

    def test_calls(self):
        rule = [dict(name="strptime", kind="calls")]
        self.assertEqual(grader.ast_problems('datetime.strptime("x", "y")\n', rule), [])
        self.assertEqual(grader.ast_problems('strptime("x", "y")\n', rule), [])
        self.assertEqual(len(grader.ast_problems("print(11, 3)\n# strptime\n", rule)), 1)

    def test_syntax_error_left_to_run(self):
        self.assertEqual(grader.ast_problems("def (\n", [dict(name="money", kind="imports", names=["fmt"])]), [])


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_docs_right(self):
        answer("docs.txt", ["B", "C", "A"])
        out = ev(["docs"])
        self.assertTrue(all(oks(out)), details(out))

    def test_docs_common_mistakes(self):
        """%b 以為是兩位數的月、randint 以為跟 range 一樣不含 6、ceil 以為是小數。"""
        answer("docs.txt", ["A", "A", "C"])
        out = ev(["docs"])
        self.assertFalse(any(oks(out)), details(out))

    def test_docs_match_python(self):
        """docs.txt 每一題的程式真的跑一次，跟答案一致（randint 跑 2000 次看範圍）。"""
        import math
        import random
        key = json.loads((D / "answers" / "docs.json").read_text(encoding="utf-8"))
        self.assertEqual(date(2026, 11, 3).strftime("%b"), key["questions"][0]["choices"]["B"])
        rolls = {random.randint(1, 6) for _ in range(2000)}
        self.assertEqual(rolls, set(range(1, 7)))
        self.assertEqual(key["questions"][1]["choices"]["C"], "1 到 6")
        self.assertEqual(str(math.ceil(1250 / 3)), key["questions"][2]["choices"]["A"])
        self.assertEqual([q["accept"] for q in key["questions"]], [["B"], ["C"], ["A"]])
        for q in key["questions"]:
            self.assertIn("https://docs.python.org/3.13/", q["hint"])

    def test_imports_right(self):
        answer("imports.txt", ["B", "C", "A"])
        out = ev(["imports"])
        self.assertTrue(all(oks(out)), details(out))

    def test_imports_install_is_wrong(self):
        """第 3 題答「想辦法裝起來」或「裝名字很像的」都不對：查不到就不裝。"""
        for bad in ("B", "C"):
            answer("imports.txt", ["B", "C", bad])
            out = ev(["imports"])
            self.assertFalse(out.results[2].ok, bad)
            start()

    def test_fake_names_not_stdlib(self):
        """imports.txt 的 budgetkit、影片的 twmoney 不在標準函式庫；statistics、datetime 在（PyPI 那邊的查詢紀錄在製作稿 rec/src/pypi_check.txt）。"""
        import sys
        self.assertIn("statistics", sys.stdlib_module_names)
        self.assertIn("datetime", sys.stdlib_module_names)
        for name in ("budgetkit", "twmoney", "requests"):
            self.assertNotIn(name, sys.stdlib_module_names)

    def test_two_letters_is_not_a_choice(self):
        answer("imports.txt", ["A 或 B", "C", "A"])
        out = ev(["imports"])
        self.assertFalse(out.results[0].ok)


class Tutor(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_labels(self):
        out = ev(["tutor"])
        self.assertFalse(out.results[0].ok)

    def test_filled(self):
        p = mine("tutor.md")
        txt = p.read_text(encoding="utf-8")
        txt = (txt.replace("我問家教的：", "我問家教的：%Y、%m、%d 是不是年月日，大寫 %M 會怎樣")
                  .replace("家教怎麼說：", "家教怎麼說：方向對，叫我自己查大寫 M")
                  .replace("我在官方文件查到的：", "我在官方文件查到的：%M 是 Minute，分鐘"))
        p.write_text(txt, encoding="utf-8")
        out = ev(["tutor"])
        self.assertTrue(out.results[0].ok, details(out))


class StartFiles(unittest.TestCase):
    def test_start_main_parses(self):
        ast.parse((D / "start" / "main.py").read_text(encoding="utf-8"))
        ast.parse((D / "start" / "money.py").read_text(encoding="utf-8"))

    def test_reference_output(self):
        """正確版在沙盒真的跑：main.py 印三行（本月是今天）、money.py 印自己的檢查；兩個檔在同一個資料夾。"""
        start()
        write(mine("money.py"), REF_MONEY)
        write(mine("main.py"), REF_MAIN)
        env = grader.Env(L)
        p = env.run_file(mine("main.py"))
        self.assertEqual(p.stdout.splitlines(), ["合計 1,820 元", date.today().strftime("本月 %Y-%m"), "11 3"], p.stderr)
        p = env.run_file(mine("money.py"))
        self.assertEqual(p.stdout.splitlines(), ["money.py 自己的檢查都過了"], p.stderr)

    def test_lesson_counts(self):
        les = grader.load_lesson(LID, COURSE)
        plan = grader.plan(les, L)
        self.assertEqual(len(plan), 14)
        groups = [r.group for r in plan]
        self.assertEqual((groups.count("第一圈"), groups.count("第二圈"), groups.count("第三圈")), (7, 4, 3))


if __name__ == "__main__":
    unittest.main()
