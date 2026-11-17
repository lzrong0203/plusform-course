"""1-26〈讀別人的程式：100 行陌生程式加一個功能〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 沒有加新的東西：第①圈 delete 指令用 run 的 sandbox（1-23）＋probe（1-24）：學員的 old_ledger.py 和課程原本的三筆帳放進暫存資料夾，
餵 show、delete 2、y、show、q；probe_delete.py 載入 old_ledger.py，呼叫 COMMANDS["delete"]、看剩下哪幾筆和存進檔案的字。
第③圈：學員的 assert（try_checks，1-22）拿去跑 delete_entry 的正確版和 3 個 AI 寫錯的版本（m1 編號當索引差一、m2 沒確認也刪、m3 編號 0 刪到最後一筆）；
start/delete_ai.py 就是 m1（影片裡 AI 交回的那一版）。read.txt 10 題的答案，能跑的都真的跑一次。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

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

BASE = WS / "l126"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-26"
D = COURSE / "lessons" / LID
HEAD = ('from delete_ai import Entry, delete_entry\n\nlunch = Entry("11/03", "午餐", 120)\nbus = Entry("11/04", "公車", 15)\n'
        'dinner = Entry("11/05", "晚餐", 180)\n\nbook = [lunch, bus, dinner]\n')
WHICH = "assert delete_entry(book, 2) == bus\n"                 # 先確認：交回的是公車（抓 m1）
KEEP = "assert book == [lunch, bus, dinner]\n"                   # 沒確認，一筆都不刪（抓 m2）
DONE = "assert delete_entry(book, 2, confirm=True) == bus\nassert book == [lunch, dinner]\n"
ZERO = ('try:\n    delete_entry(book, 0, confirm=True)\nexcept ValueError:\n    pass\nelse:\n    assert False, "編號 0 應該丟 ValueError"\n')   # 抓 m3
BEAR = HEAD + WHICH + KEEP + DONE + ZERO   # 影片裡熊寫的：先確認交回公車、沒確認不刪、確認以後剩午餐和晚餐、編號 0 丟 ValueError


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
    write(mine("checks_delete.py"), text)
    return ev(["r3"])


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def run_ledger(src: str, stdin: str, data: str | None = None) -> subprocess.CompletedProcess:
    """在暫存資料夾跑一份 old_ledger.py（旁邊放課程原本的三筆帳）。"""
    t = Path(tempfile.mkdtemp(prefix="plusform-1-26-", dir=BASE))
    (t / "old_ledger.py").write_text(src, encoding="utf-8")
    (t / "old_ledger.txt").write_text(data if data is not None else (D / "start" / "old_ledger.txt").read_text(encoding="utf-8"), encoding="utf-8")
    return subprocess.run([sys.executable, "-B", "old_ledger.py"], cwd=t, input=stdin, capture_output=True, text=True, timeout=10)


START = (D / "start" / "old_ledger.py").read_text(encoding="utf-8")
DELETE_REF = ('@command\ndef delete(entries, arg):\n    no = int(arg)\n    e = entries.pop(no - 1)\n    save(entries)\n'
              '    print("刪掉了：", fmt(no, e))\n')


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Program(unittest.TestCase):
    def test_about_100_lines(self):
        """起點檔大約一百行（影片說「大約一百行」），正確版只多 delete 那一段。"""
        n = len(START.splitlines())
        self.assertTrue(100 <= n <= 115, n)
        self.assertEqual(ref("old_ledger.py").replace("\n\n" + DELETE_REF, ""), START)

    def test_start_runs(self):
        """影片開場與第①圈跑的：show、total、看不懂的 add（WARNING 在 stderr）、q。"""
        p = run_ledger(START, "show\ntotal\nadd 11/06 咖啡 八十五\nq\n")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, "可以打的指令：show、add、total、q\n> 1. 11/03 午餐 120\n2. 11/04 公車 15\n3. 11/05 晚餐 180\n"
                                   "> 合計 315 元\n> > ")
        self.assertEqual(p.stderr, "WARNING:root:看不懂：11/06 咖啡 八十五\n")

    def test_reference_delete(self):
        p = run_ledger(ref("old_ledger.py"), "show\ndelete 2\nshow\ntotal\nq\n")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("可以打的指令：show、add、total、delete、q", p.stdout)
        self.assertIn("> 刪掉了： 2. 11/04 公車 15\n> 1. 11/03 午餐 120\n2. 11/05 晚餐 180\n> 合計 300 元", p.stdout)

    def test_bad_line_in_file_warns(self):
        """read_entries 遇到看不懂的一行：logging.warning 印出第幾行、跳過，其他照讀。"""
        p = run_ledger(START, "show\nq\n", data="11/03 午餐 120\n11/04 公車 十五\n11/05 晚餐 180\n")
        self.assertEqual(p.stderr, "WARNING:root:第 2 行看不懂，跳過\n")
        self.assertIn("1. 11/03 午餐 120\n2. 11/05 晚餐 180", p.stdout)


class Read(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("read.txt", ["B", "A", "C", "A", "A", "C", "B", "B", "A", "B"])
        out = ev(["read"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(len(out.results), 10)

    def test_common_mistakes(self):
        """從第 1 行讀起、以為 add 會讀檔、把 @ 想反、以為 Python 自己找同名函式、yield 當成 return、日期在後面也行、以為會當掉、info 會印、編號當索引。"""
        answer("read.txt", ["A", "B", "A", "B", "C", "A", "C", "A", "B", "A"])
        out = ev(["read"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_answers_match_python(self):
        """能跑的都真的跑：@ 等於 f = command(f)、COMMANDS 用名字查得到、yield 一次一筆、re 只對得上 B、WARNING 照樣子印、info 不印、第 2 筆是 entries[1]。"""
        key = json.loads((D / "answers" / "read.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"][0] for q in key["questions"]], ["B", "A", "C", "A", "A", "C", "B", "B", "A", "B"])
        code = r'''
import io, logging, re, contextlib, sys
sys.path.insert(0, sys.argv[1])
import old_ledger as L
print(sorted(L.COMMANDS), L.COMMANDS["total"] is L.total)
def plain(entries, arg):
    return "x"
plain2 = L.command(plain)
print(plain2 is plain, "plain" in L.COMMANDS)
g = L.read_entries(L.DATA)
print(type(g).__name__, next(g).item, next(g).item)
print([bool(L.LINE.fullmatch(s)) for s in ["11/06 咖啡 八十五", "11/06 咖啡 85", "咖啡 11/06 85"]])
logging.info("讀了 3 筆")
entries = L.load()
show = io.StringIO()
with contextlib.redirect_stdout(show):
    L.show(entries, "")
second = show.getvalue().splitlines()[1]
print(second, "|", L.fmt(2, entries[1]))
'''
        p = subprocess.run([sys.executable, "-B", "-c", code, str(D / "start")], capture_output=True, text=True)
        self.assertEqual(p.stderr, "")
        self.assertEqual(p.stdout.splitlines(), [
            "['add', 'show', 'total'] True",
            "True True",
            "generator 午餐 公車",
            "[False, True, False]",
            "2. 11/04 公車 15 | 2. 11/04 公車 15",
        ])

    def test_load_calls_read_entries_add_calls_parse_save(self):
        """呼叫圖（第 2、3 題）：照 ast 找每個函式裡呼叫的名字。"""
        import ast
        tree = ast.parse(START)
        calls = {f.name: sorted({n.func.id for n in ast.walk(f) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)})
                 for f in tree.body if isinstance(f, ast.FunctionDef)}
        self.assertEqual(calls["load"], ["len", "list", "read_entries"])
        self.assertEqual(calls["read_entries"], ["enumerate", "open", "parse"])
        self.assertEqual(calls["add"], ["fmt", "len", "parse", "print", "save"])
        self.assertEqual(calls["main"], ["input", "len", "load", "print"])


class DeleteRun(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_fails(self):
        out = ev(["delete-1", "delete-2"])
        self.assertFalse(any(r.ok for r in out.results))
        self.assertIn("沒有這個指令： delete", out.results[0].detail)

    def test_reference_passes(self):
        write(mine("old_ledger.py"), ref("old_ledger.py"))
        out = ev(["delete-1", "delete-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_does_not_touch_students_data(self):
        """check 用暫存資料夾跑：學員的 old_ledger.txt 一個字都不動，也不會多出 probe_delete.py。"""
        write(mine("old_ledger.py"), ref("old_ledger.py"))
        write(mine("old_ledger.txt"), "11/09 書 450\n")
        out = ev(["delete-1", "delete-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(mine("old_ledger.txt").read_text(encoding="utf-8"), "11/09 書 450\n")
        self.assertFalse(mine("probe_delete.py").exists())

    def test_off_by_one(self):
        """寫成 entries.pop(no)：刪到第 3 筆（晚餐），兩題都抓得到。"""
        write(mine("old_ledger.py"), ref("old_ledger.py").replace("entries.pop(no - 1)", "entries.pop(no)"))
        out = ev(["delete-1", "delete-2"])
        self.assertFalse(out.results[0].ok)
        self.assertFalse(out.results[1].ok)

    def test_without_command_decorator(self):
        """忘了 @command：COMMANDS 裡沒有 delete，main 說沒有這個指令。"""
        write(mine("old_ledger.py"), ref("old_ledger.py").replace("@command\ndef delete", "def delete"))
        out = ev(["delete-1", "delete-2"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("沒有這個指令： delete", out.results[0].detail)
        self.assertFalse(out.results[1].ok)

    def test_without_save(self):
        """刪完沒有 save：畫面上看起來刪了（delete-1 過），檔案還是三筆（probe 抓得到）。"""
        write(mine("old_ledger.py"), ref("old_ledger.py").replace("    e = entries.pop(no - 1)\n    save(entries)\n", "    e = entries.pop(no - 1)\n"))
        out = ev(["delete-1", "delete-2"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)
        self.assertFalse(out.results[1].ok)

    def test_without_int(self):
        """沒有 int(arg)：pop("2") 是 TypeError，main 沒接住就當掉。"""
        write(mine("old_ledger.py"), ref("old_ledger.py").replace("    no = int(arg)\n", "    no = arg\n").replace("entries.pop(no - 1)", "entries.pop(no)"))
        out = ev(["delete-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("TypeError", out.results[0].detail)

    def test_with_confirm_passes(self):
        """多做一步「確認」（input 問 y/n）也算對：check 有餵 y。"""
        confirm = DELETE_REF.replace("    e = entries.pop(no - 1)\n", "    if input(f\"要刪掉 {fmt(no, entries[no - 1])} 嗎？(y/n) \") != \"y\":\n        return\n    e = entries.pop(no - 1)\n")
        write(mine("old_ledger.py"), START.replace("\n\ndef main():", "\n\n" + confirm + "\n\ndef main():"))
        out = ev(["delete-1", "delete-2"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        quiet = confirm.replace('    print("刪掉了：", fmt(no, e))\n', "")   # 問了 y/n、刪完什麼都不印：下一個提示「> 」接在問句後面，也要認得
        write(mine("old_ledger.py"), START.replace("\n\ndef main():", "\n\n" + quiet + "\n\ndef main():"))
        out = ev(["delete-1"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)


class Tutor(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_then_filled(self):
        out = ev(["tutor"])
        self.assertFalse(out.results[0].ok)
        p = mine("tutor.md")
        txt = p.read_text(encoding="utf-8")
        for lab in ("家教出的三題：", "我的回答：", "它說哪裡不對：", "我回去對照看到的："):
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
        """交回的是公車抓 m1；沒確認不刪抓 m2；編號 0 丟 ValueError 抓 m3。"""
        def caught(body):
            out = r3(HEAD + body)
            return [part(out, f"m{k}").ok for k in (1, 2, 3)]
        self.assertEqual(caught(WHICH + "assert len(book) >= 2\nassert len(book) <= 3\n"), [True, False, False])
        self.assertEqual(caught("delete_entry(book, 2)\n" + KEEP + "assert len(book) == 3\nassert book[0] == lunch\n"), [False, True, False])
        self.assertEqual(caught(ZERO + "assert len(book) == 3\nassert book[0] == lunch\n"), [False, False, True])

    def test_start_example_catches_none(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
        self.assertEqual([part(out, f"m{k}").ok for k in (1, 2, 3)], [False, False, False])

    def test_start_version_is_m1(self):
        self.assertEqual("".join((D / "start" / "delete_ai.py").read_text(encoding="utf-8").splitlines(keepends=True)[1:]),
                         "".join((D / "mutants" / "delete_ai_m1.py").read_text(encoding="utf-8").splitlines(keepends=True)[1:]))

    def test_bear_checks_on_ai_version(self):
        """影片裡熊的檢查，拿去跑 AI 交回的 delete_ai.py（差一的那一版）：第一條 assert 就 AssertionError；
        delete_entry(book, 2) 交回的是晚餐。課程的正確版：什麼都沒印。"""
        with tempfile.TemporaryDirectory(dir=BASE) as t:
            shutil.copyfile(D / "start" / "delete_ai.py", Path(t) / "delete_ai.py")
            Path(t, "checks_delete.py").write_text(BEAR, encoding="utf-8")
            p = subprocess.run([sys.executable, "-B", "checks_delete.py"], cwd=t, capture_output=True, text=True)
            self.assertEqual(p.returncode, 1)
            self.assertTrue(p.stderr.rstrip().endswith("AssertionError"), p.stderr)
            self.assertIn("assert delete_entry(book, 2) == bus", p.stderr)
            q = subprocess.run([sys.executable, "-B", "-c", "from delete_ai import *\nb = [Entry('11/03','午餐',120), Entry('11/04','公車',15), Entry('11/05','晚餐',180)]\n"
                                "print(delete_entry(b, 2))"], cwd=t, capture_output=True, text=True)
            self.assertEqual(q.stdout, "Entry(date='11/05', item='晚餐', amount=180)\n")
            shutil.copyfile(D / "reference" / "delete_ai.py", Path(t) / "delete_ai.py")
            p = subprocess.run([sys.executable, "-B", "checks_delete.py"], cwd=t, capture_output=True, text=True)
            self.assertEqual((p.returncode, p.stdout, p.stderr), (0, "", ""))

    def test_zero_deletes_last_without_check(self):
        """m3 與第①圈的 delete：編號 0 時 pop(0 - 1) 刪到最後一筆、什麼都沒說。"""
        p = run_ledger(ref("old_ledger.py"), "delete 0\nshow\nq\n")
        self.assertIn("刪掉了： 0. 11/05 晚餐 180", p.stdout)
        self.assertNotIn("晚餐", p.stdout.split("刪掉了")[1].split("\n", 1)[1])


if __name__ == "__main__":
    unittest.main()
