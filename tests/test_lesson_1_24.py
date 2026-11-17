"""1-24〈類別與物件：Entry、Ledger、@dataclass〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 加的東西（只對寫了它的題目生效）：run 的 sandbox 加 probe（課程準備的小程式 tests/probe_entry.py、probe_ledger.py 複製進暫存資料夾，
import 學員的 entry.py／ledger.py，另外做幾筆帳試試看：屬性、印出來的樣子、== 比每個欄位、少給金額 TypeError；兩本帳本各有自己的 entries、total）。
第③圈：學員的 assert 拿去跑 biggest 的正確版和 3 個 AI 寫錯的版本（m1 交回最後一筆、m2 空的帳本當掉、m3 方向寫反）；
start/ledger_ai.py 是 AI 多做了繼承架構的版本（biggest 對、測試會過），收不收在 review.txt（對答）判。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l124"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-24"
D = COURSE / "lessons" / LID
CK_HEAD = "from ledger_ai import Entry, Ledger\n\nbook = Ledger()\n"
EMPTY = "assert book.biggest() is None\n"
ONE = 'book.add(Entry("11/03", "午餐", 120))\nassert book.biggest() == Entry("11/03", "午餐", 120)\n'
THREE = ('book.add(Entry("11/05", "晚餐", 180))\nbook.add(Entry("11/04", "公車", 15))\n'
         'assert book.biggest() == Entry("11/05", "晚餐", 180)\n')
BEAR = CK_HEAD + EMPTY + ONE + THREE   # 影片裡熊寫的三條：空的、一筆、三筆裡最大的在中間


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


def ref(name: str) -> str:
    """正確版（去掉第一行老師的說明）。"""
    return "".join((D / "reference" / name).read_text(encoding="utf-8").splitlines(keepends=True)[1:])


def ev(ids: list[str], ledger: Path | None = L) -> grader.Outcome:
    les = grader.load_lesson(LID, COURSE)
    return grader.evaluate(les, ledger, only=[c for c in les.checks if c["id"] in ids])


def part(out: grader.Outcome, suffix: str) -> grader.Result:
    return next(r for r in out.results if r.id == suffix or (r.id.startswith("r3") and r.id.rsplit("-", 1)[-1] == suffix))


def r3(text: str) -> grader.Outcome:
    write(mine("checks_ledger.py"), text)
    return ev(["r3"])


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def quiz_code(name: str, k: int) -> str:
    """作答檔第 k 題的程式（「#   」開頭、不是選項的那幾行）。"""
    blk = (D / "start" / name).read_text(encoding="utf-8").split("\n答：")[k - 1].split("題：")[-1].splitlines()
    code = [ln[4:] for ln in blk if ln.startswith("#   ") and not ln.startswith(("#   A.", "#   B.", "#   C."))]
    return "\n".join(code) + "\n"


ENTRY_DEF = ("from dataclasses import dataclass\n\n@dataclass\nclass Entry:\n    date: str\n    item: str\n    amount: int\n\n")


def run_quiz(code: str, with_entry: bool = True) -> tuple[str, str]:
    """跑作答檔裡的一段程式，回傳（印出來的, 錯誤的名字）。"""
    buf = io.StringIO()
    err = ""
    with contextlib.redirect_stdout(buf):
        try:
            exec(compile((ENTRY_DEF if with_entry else "") + code, "<q>", "exec"), {"__name__": "__main__"})
        except Exception as e:   # noqa: BLE001
            err = type(e).__name__
    return buf.getvalue(), err


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Predict(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("predict.txt", ["C", "B", "A"])
        out = ev(["predict"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_common_mistakes(self):
        """以為少給的欄位會變成 None、以為一樣的兩筆一定相等、以為改 bus 會動到 lunch。"""
        answer("predict.txt", ["B", "A", "B"])
        out = ev(["predict"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_answers_match_python(self):
        """三題都真的跑一次：少給金額 TypeError、沒有 @dataclass 的 == 是 False、改 bus 不動到 lunch。"""
        key = json.loads((D / "answers" / "predict.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"] for q in key["questions"]], [["C"], ["B"], ["A"]])
        self.assertEqual(run_quiz(quiz_code("predict.txt", 1)), ("", "TypeError"))
        self.assertEqual(run_quiz(quiz_code("predict.txt", 2), with_entry=False), ("False\n", ""))
        self.assertEqual(run_quiz(quiz_code("predict.txt", 3)), ("120\n", ""))


class EntryRun(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_fails(self):
        out = ev(["entry-1", "entry-2"])
        self.assertFalse(any(r.ok for r in out.results))
        self.assertIn("NameError", out.results[0].detail)

    def test_reference_passes(self):
        write(mine("entry.py"), ref("entry.py"))
        out = ev(["entry-1", "entry-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_without_dataclass_shows_object_repr(self):
        """忘了 @dataclass：只寫欄位的 class 做不出物件（TypeError: Entry() takes no arguments）。"""
        write(mine("entry.py"), ref("entry.py").replace("@dataclass\n", ""))
        out = ev(["entry-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("TypeError", out.results[0].detail)

    def test_plain_init_fails_repr_and_eq(self):
        """自己寫 __init__、沒有 @dataclass：屬性對，可是印出來看不到欄位、一樣的兩筆 == 是 False，probe 抓得到。"""
        plain = ref("entry.py").replace(
            "@dataclass\nclass Entry:\n    date: str\n    item: str\n    amount: int\n",
            "class Entry:\n    def __init__(self, date, item, amount):\n        self.date = date\n        self.item = item\n        self.amount = amount\n")
        self.assertNotIn("@dataclass\nclass", plain)
        write(mine("entry.py"), plain)
        out = ev(["entry-2"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("屬性： 12/01 書 450", out.results[0].detail)
        self.assertIn("一樣的兩筆用 == 比： False", out.results[0].detail)
        self.assertIn("課程準備的小程式 probe_entry.py", out.results[0].detail)

    def test_hardcoded_prints_caught_by_probe(self):
        """把三行直接 print 出來、Entry 隨便寫：entry-1 過了，entry-2（另外做 12/01 書 450）抓得到。"""
        fake = ("from dataclasses import dataclass\n\n\nclass Entry:\n    def __init__(self, *a):\n        pass\n\n\n"
                "print(\"Entry(date='11/03', item='午餐', amount=120)\")\nprint('公車 15')\nprint(135)\n")
        write(mine("entry.py"), fake)
        out = ev(["entry-1", "entry-2"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)
        self.assertFalse(out.results[1].ok)

    def test_field_order_matters(self):
        """欄位順序寫錯（item 在 date 前面）：印出來的樣子和屬性都不對。"""
        write(mine("entry.py"), ref("entry.py").replace("    date: str\n    item: str\n", "    item: str\n    date: str\n"))
        out = ev(["entry-1", "entry-2"])
        self.assertFalse(out.results[0].ok)
        self.assertFalse(out.results[1].ok)

    def test_probe_ignores_students_prints(self):
        """probe 載入 entry.py 時，最下面自己印的三行不會混進 check 比的字。"""
        write(mine("entry.py"), ref("entry.py") + 'print("多印一行")\n')
        out = ev(["entry-2"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_probe_does_not_touch_ledger(self):
        """probe 在暫存資料夾跑：學員帳本的 lessons/1-24 不會多出 probe_entry.py。"""
        write(mine("entry.py"), ref("entry.py"))
        ev(["entry-2"])
        self.assertFalse(mine("probe_entry.py").exists())


class LedgerRun(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_fails(self):
        out = ev(["ledger-1", "ledger-2"])
        self.assertFalse(any(r.ok for r in out.results))

    def test_reference_passes(self):
        write(mine("ledger.py"), ref("ledger.py"))
        out = ev(["ledger-1", "ledger-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_class_variable_shared(self):
        """entries 寫在 class 下面（影片第②圈熊第一次寫的）：兩本帳本共用，印出 2 2；probe 的 b 也看得到 a 加的（連 ledger.py 最下面加的一共 4 筆）。"""
        shared = ref("ledger.py").replace("    def __init__(self):\n        self.entries = []\n\n", "    entries = []\n\n")
        write(mine("ledger.py"), shared)
        out = ev(["ledger-1", "ledger-2"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("2 2", out.results[0].detail)
        self.assertFalse(out.results[1].ok)
        self.assertIn("b 有幾筆： 4", out.results[1].detail)   # ledger.py 最下面 nov 加的兩筆也在同一個 list

    def test_dataclass_default_factory_passes(self):
        """用 @dataclass＋field(default_factory=list) 寫帳本也算對。"""
        dc = ref("ledger.py").replace("from dataclasses import dataclass\n", "from dataclasses import dataclass, field\n").replace(
            'class Ledger:\n    """一本帳本：裡面放很多筆 Entry。"""\n\n    def __init__(self):\n        self.entries = []\n',
            '@dataclass\nclass Ledger:\n    """一本帳本：裡面放很多筆 Entry。"""\n\n    entries: list = field(default_factory=list)\n')
        self.assertIn("default_factory", dc)
        write(mine("ledger.py"), dc)
        out = ev(["ledger-1", "ledger-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_dataclass_list_default_message(self):
        """@dataclass 的欄位寫 = []：Python 直接 ValueError（README 常見錯誤的原文）。"""
        bad = ("from dataclasses import dataclass\n\n@dataclass\nclass Ledger:\n    entries: list = []\n")
        p = subprocess.run([sys.executable, "-B", "-c", bad], capture_output=True, text=True)
        self.assertIn("ValueError: mutable default <class 'list'> for field entries is not allowed: use default_factory", p.stderr)

    def test_total_without_return(self):
        """total 只 print 不 return：ledger-1 印出 None，抓得到。"""
        write(mine("ledger.py"), ref("ledger.py").replace("        return s\n", "        print(s)\n"))
        out = ev(["ledger-1"])
        self.assertFalse(out.results[0].ok)

    def test_add_without_self(self):
        """def add(entry): 少了 self：TypeError，crash_story 會說出來。"""
        write(mine("ledger.py"), ref("ledger.py").replace("def add(self, entry):", "def add(entry):"))
        out = ev(["ledger-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("TypeError", out.results[0].detail)


class Tutor(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_then_filled(self):
        out = ev(["tutor"])
        self.assertFalse(out.results[0].ok)
        p = mine("tutor.md")
        txt = p.read_text(encoding="utf-8")
        for lab in ("我先寫的：", "家教怎麼說：", "我跑出來的：", "我最後改成："):
            txt = txt.replace(lab + "\n", lab + "寫了一些字\n", 1)
        p.write_text(txt, encoding="utf-8")
        out = ev(["tutor"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)


class R3(unittest.TestCase):
    def setUp(self):
        start()

    def test_bear_checks_catch_all(self):
        out = r3(BEAR)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_each_check_catches(self):
        """空的帳本抓 m2；最大的在中間抓 m1（最後一筆）和 m3（最小的）。"""
        def caught(body):
            out = r3(CK_HEAD + ONE + body + 'assert book.biggest().amount >= 120\n')
            return [part(out, f"m{k}").ok for k in (1, 2, 3)]
        self.assertEqual(caught(""), [False, False, False])
        self.assertEqual(caught(THREE), [True, False, True])
        out = r3(CK_HEAD + EMPTY + ONE + 'assert book.biggest().item == "午餐"\n')
        self.assertEqual([part(out, f"m{k}").ok for k in (1, 2, 3)], [False, True, False])

    def test_start_example_catches_none(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
        self.assertEqual([part(out, f"m{k}").ok for k in (1, 2, 3)], [False, False, False])

    def test_bear_checks_pass_on_ai_version(self):
        """影片裡熊的三條，拿去跑 AI 交回的 ledger_ai.py（多做了繼承架構的那一份）：全部成立（什麼都沒印）。"""
        with tempfile.TemporaryDirectory() as t:
            shutil.copyfile(D / "start" / "ledger_ai.py", Path(t) / "ledger_ai.py")
            Path(t, "checks_ledger.py").write_text(BEAR, encoding="utf-8")
            p = subprocess.run([sys.executable, "-B", "checks_ledger.py"], cwd=t, capture_output=True, text=True)
            self.assertEqual((p.returncode, p.stdout, p.stderr), (0, "", ""))


class Review(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("review.txt", ["C", "A", "B"])
        out = ev(["review"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_accept_because_tests_pass_is_wrong(self):
        answer("review.txt", ["A", "B", "A"])
        out = ev(["review"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_answers_match_python(self):
        """第 2、3 題真的跑 start/ledger_ai.py：MonthlyLedger 有 Ledger 的 biggest；12/01 那一筆默默沒收、沒有錯誤。"""
        key = json.loads((D / "answers" / "review.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"] for q in key["questions"]], [["C"], ["A"], ["B"]])
        code = ("import sys; sys.path.insert(0, sys.argv[1]); from ledger_ai import Entry, Ledger, MonthlyLedger\n"
                "book = MonthlyLedger('11'); book.add(Entry('12/01', '書', 450)); print(len(book.entries), book.biggest())\n"
                "print(issubclass(MonthlyLedger, Ledger), MonthlyLedger.biggest is Ledger.biggest)")
        p = subprocess.run([sys.executable, "-B", "-c", code, str(D / "start")], capture_output=True, text=True)
        self.assertEqual((p.stdout, p.stderr), ("0 None\nTrue True\n", ""))


if __name__ == "__main__":
    unittest.main()
