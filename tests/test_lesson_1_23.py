"""1-23〈檔案讀寫：關掉程式，帳還在〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 加的東西（只對寫了它的題目生效）：run 的 sandbox（學員的檔複製到暫存資料夾擺成「帳本最上層／lessons/1-23」照步驟跑，
可以從不同資料夾跑、檢查寫出來的 ledger.txt 內容與位置；學員帳本裡真的 ledger.txt 一個都不動）；ast_require 的 with_open、open_utf8；
chaff assert 模式的 tmp_cwd（學員的來回測試在暫存資料夾跑，測試檔不寫進帳本）、min_crash_marks（至少一行標「已知會當掉」）、mark_note。
第③圈：學員的來回測試拿去跑課程版本 store.py 和 3 個 AI 寫錯的版本（m1 存檔用 a、m2 只讀第一行、m3 空的帳本不存）；
備註有逗號那一條連課程版本都會當掉（ValueError: too many values to unpack），標「# 已知會當掉」記下來，不用修（2-4 用 CSV 解決）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l123"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-23"
D = COURSE / "lessons" / LID
HEAD = ("from pathlib import Path\n\nfrom store import load_entries, save_entries\n\n"
        "TEST = Path(__file__).parent / \"roundtrip_test.txt\"\n\n\n"
        "def roundtrip(entries):\n    save_entries(TEST, entries)\n    return load_entries(TEST)\n\n\n")
A1 = 'a = [("11/03", "午餐", 120, "跟同事")]\nassert roundtrip(a) == a\n'
B2 = 'b = [("11/03", "午餐", 120, "跟同事"), ("11/04", "公車", 15, "")]\nassert roundtrip(b) == b\n'
E0 = "assert roundtrip([]) == []\n"
COMMA = 'c = [("11/05", "聚餐", 600, "跟小明, 小華")]\nassert roundtrip(c) == c'
BEAR = HEAD + A1 + B2 + E0 + COMMA + "   # 已知會當掉：備註有逗號，2-4 用 CSV 解決\n"   # 影片裡熊寫的（好幾筆、空的、逗號標起來）


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
    for stray in (L / "ledger.txt",):
        if stray.exists():
            stray.unlink()
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
    write(mine("checks_store.py"), text)
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
    while code and code[0].startswith(" "):   # 前面「原本的內容」那幾行（多空兩格）不是程式
        code.pop(0)
    return "\n".join(code) + "\n"


def run_in(folder: Path, code: str) -> str:
    buf = io.StringIO()
    old = Path.cwd()
    os.chdir(folder)
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<q>", "exec"), {})
    finally:
        os.chdir(old)
    return buf.getvalue()


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Predict(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("predict.txt", ["B", "C", "A"])
        out = ev(["predict"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_common_mistakes(self):
        """以為 w 會接在後面、以為 a 也會清空、以為檔案一定跟著 .py 檔。"""
        answer("predict.txt", ["A", "A", "B"])
        out = ev(["predict"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_answers_match_python(self):
        """第 1、2 題真的跑一次（暫存資料夾裡擺好 ledger.txt）：w 剩 1 行、a 跑兩次是 2 行；第 3 題用子程序從不同資料夾跑。"""
        key = json.loads((D / "answers" / "predict.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"] for q in key["questions"]], [["B"], ["C"], ["A"]])
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "ledger.txt").write_text("11/03,午餐,120\n11/04,公車,15\n", encoding="utf-8")
            run_in(t, quiz_code("predict.txt", 1))
            self.assertEqual((t / "ledger.txt").read_text(encoding="utf-8").splitlines(), ["11/05,晚餐,180"])
            (t / "ledger.txt").write_text("", encoding="utf-8")
            run_in(t, quiz_code("predict.txt", 2))
            run_in(t, quiz_code("predict.txt", 2))
            self.assertEqual((t / "ledger.txt").read_text(encoding="utf-8").splitlines(), ["11/05,晚餐,180"] * 2)
            les = t / "lessons" / "1-23"
            les.mkdir(parents=True)
            (les / "save.py").write_text('with open("ledger.txt", "w", encoding="utf-8") as f:\n    f.write("x\\n")\n', encoding="utf-8")
            subprocess.run([sys.executable, "-B", "lessons/1-23/save.py"], cwd=t, check=True)
            self.assertTrue((t / "ledger.txt").exists())
            self.assertFalse((les / "ledger.txt").exists())


class Save(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_fails(self):
        out = ev(["save-1"])
        self.assertFalse(out.results[0].ok)

    def test_reference_passes_and_ledger_untouched(self):
        """正確版過；學員帳本裡原本的 ledger.txt（真的帳）一個字都不動，帳本最上層也不多出檔案。"""
        write(mine("save.py"), ref("save.py"))
        real = write(mine("ledger.txt"), "11/01,早餐,65\n")
        out = ev(["save-1"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)
        self.assertEqual(real.read_text(encoding="utf-8"), "11/01,早餐,65\n")
        self.assertFalse((L / "ledger.txt").exists())

    def test_relative_path_lands_on_top(self):
        write(mine("save.py"), ref("save.py").replace('Path(__file__).parent / "ledger.txt"', '"ledger.txt"'))
        out = ev(["save-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("沒有出現", out.results[0].detail)
        self.assertFalse((L / "ledger.txt").exists())   # 在暫存資料夾跑的，帳本最上層也沒有

    def test_relative_path_message_when_file_also_there(self):
        """相對路徑的寫法另外又寫了一份在旁邊（老師端的特例）：最上層多出來的那一份要報出來。"""
        src = ref("save.py").replace('with open(p,', 'with open("ledger.txt", "w", encoding="utf-8") as g:\n    g.write("x\\n")\nwith open(p,')
        write(mine("save.py"), src)
        out = ev(["save-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("跑到帳本最上層去了", out.results[0].detail)

    def test_missing_encoding(self):
        write(mine("save.py"), ref("save.py").replace(', encoding="utf-8"', ""))
        out = ev(["save-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn('encoding="utf-8"', out.results[0].detail)
        self.assertIn("Windows", out.results[0].detail)

    def test_open_without_with(self):
        src = ref("save.py").replace('with open(p, "w", encoding="utf-8") as f:\n    for', 'f = open(p, "w", encoding="utf-8")\nif True:\n    for').replace(
            'print("存好了")', 'f.close()\nprint("存好了")')
        write(mine("save.py"), src)
        out = ev(["save-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("with 後面", out.results[0].detail)

    def test_missing_newline(self):
        write(mine("save.py"), ref("save.py").replace("\\n\")", "\")"))
        out = ev(["save-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("內容跟應該的不一樣", out.results[0].detail)


class Read(unittest.TestCase):
    def setUp(self):
        start()
        write(mine("save.py"), ref("save.py"))

    def test_reference_passes(self):
        write(mine("read.py"), ref("read.py"))
        out = ev(["read-1", "roundtrip"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_start_read_fails(self):
        out = ev(["read-1"])
        self.assertFalse(out.results[0].ok)

    def test_no_int_crashes(self):
        write(mine("read.py"), ref("read.py").replace("total += int(amount)", "total += amount"))
        out = ev(["read-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("TypeError", out.results[0].detail)

    def test_hardcoded_prints_caught_by_roundtrip(self):
        fake = 'print("11/03 午餐 120 元")\nprint("11/04 公車 15 元")\nprint("11/05 晚餐 180 元")\nprint("合計 315 元")\n'
        write(mine("read.py"), "from pathlib import Path\n\np = Path(__file__).parent / \"ledger.txt\"\nwith open(p, encoding=\"utf-8\") as f:\n    pass\n" + fake)
        self.assertTrue(ev(["read-1"]).results[0].ok)
        out = ev(["roundtrip"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("12/01 書 450 元", out.results[0].detail)

    def test_append_mode_caught_by_roundtrip(self):
        write(mine("save.py"), ref("save.py").replace('"w"', '"a"'))
        write(mine("read.py"), ref("read.py"))
        self.assertTrue(ev(["save-1"]).results[0].ok)   # 只存一次看不出來
        out = ev(["roundtrip"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("11/03 午餐 120 元", out.results[0].detail)
        self.assertIn("換成一筆", out.results[0].detail)

    def test_relative_read_path_caught_from_top(self):
        """read.py 的 p 還是相對路徑：進 lessons/1-23 跑找得到（read-1 過），從帳本最上層跑就 FileNotFoundError（roundtrip 抓到）。"""
        write(mine("read.py"), ref("read.py").replace('Path(__file__).parent / "ledger.txt"', '"ledger.txt"'))
        self.assertTrue(ev(["read-1"]).results[0].ok)
        out = ev(["roundtrip"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("FileNotFoundError", out.results[0].detail)

    def test_save_crash_reported_as_step_one(self):
        write(mine("save.py"), ref("save.py").replace("f.write(", "f.writ("))
        write(mine("read.py"), ref("read.py"))
        out = ev(["read-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("第 1 步就沒過", out.results[0].detail)
        self.assertIn("uv run lessons/1-23/save.py", out.results[0].detail)

    def test_entries_removed(self):
        write(mine("save.py"), ref("save.py").replace("entries = [", "rows = [").replace("in entries", "in rows"))
        write(mine("read.py"), ref("read.py"))
        out = ev(["roundtrip"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("找不到 entries", out.results[0].detail)


class Close(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("close.txt", ["B", "C", "A"])
        out = ev(["close"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_answers_match_python(self):
        """第 1 題真的跑：with 還沒結束時讀檔案是空的；第 2 題：with 跑完 f.closed 是 True。"""
        code = quiz_code("close.txt", 1)
        with tempfile.TemporaryDirectory() as t:
            printed = run_in(Path(t), code)
            self.assertEqual(printed, "''\n")
            ns: dict = {}
            old = Path.cwd()
            os.chdir(t)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(code, "<q>", "exec"), ns)
            finally:
                os.chdir(old)
            self.assertTrue(ns["f"].closed)
            self.assertEqual((Path(t) / "note.txt").read_text(encoding="utf-8"), "11/03,午餐,120\n")


class Tutor(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_then_filled(self):
        out = ev(["tutor"])
        self.assertFalse(out.results[0].ok)
        p = mine("tutor.md")
        txt = p.read_text(encoding="utf-8")
        for lab in ("家教問我的：", "我一開始的回答：", "我跑出來的：", "家教怎麼說："):
            txt = txt.replace(lab + "\n", lab + "寫了一些字\n", 1)
        p.write_text(txt, encoding="utf-8")
        out = ev(["tutor"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)


class R3(unittest.TestCase):
    def setUp(self):
        start()

    def test_bear_checks_catch_all_and_mark(self):
        out = r3(BEAR)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        mark = next(r for r in out.results if r.special)
        self.assertIn("too many values to unpack", mark.note)
        self.assertIn("2-4", mark.note)
        self.assertFalse(mine("roundtrip_test.txt").exists())   # 在暫存資料夾跑，帳本裡沒有測試檔

    def test_each_check_catches(self):
        """好幾筆抓 m1（同一個檔存第二次）和 m2（只讀第一行）；空的帳本抓 m3。"""
        def caught(body):
            out = r3(HEAD + A1 + body + 'z = [("11/06", "早餐", 65, "自己")]\nassert roundtrip(z) == z\n')
            return [part(out, f"m{k}").ok for k in (1, 2, 3)]
        self.assertEqual(caught(B2), [True, True, False])
        self.assertEqual(caught(E0), [True, False, True])

    def test_start_example_catches_none(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
        self.assertEqual([part(out, f"m{k}").ok for k in (1, 2, 3)], [False, False, False])
        self.assertFalse(part(out, "scrash").ok)
        self.assertIn("備註裡有逗號", part(out, "scrash").detail)

    def test_comma_without_mark_crashes_on_reference(self):
        out = r3(HEAD + A1 + B2 + E0 + COMMA + "\n")
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("已知會當掉", part(out, "wheat").detail)
        self.assertIn("too many values to unpack", part(out, "wheat").detail)

    def test_mark_on_normal_line_rejected(self):
        out = r3(HEAD + A1 + B2 + E0.rstrip("\n") + "   # 已知會當掉\n")
        mark = next(r for r in out.results if r.special)
        self.assertFalse(mark.ok)
        self.assertIn("並不會當掉", mark.detail)

    def test_mode_unchanged_for_other_lessons(self):
        """沒寫 tmp_cwd、min_crash_marks 的課（1-22）照舊。"""
        les = grader.load_lesson("1-22", COURSE)
        spec = next(c for c in les.checks if c["id"] == "r3")
        self.assertNotIn("tmp_cwd", spec)
        self.assertNotIn("min_crash_marks", spec)

    def test_comma_message_is_real(self):
        """影片與 README 的錯誤訊息原文：課程版本讀到備註有逗號的那一行。"""
        with tempfile.TemporaryDirectory() as t:
            p = subprocess.run([sys.executable, "-B", "-c",
                                "import sys; sys.path.insert(0, sys.argv[1]); from store import save_entries, load_entries\n"
                                "save_entries('x.txt', [('11/05', '聚餐', 600, '跟小明, 小華')]); load_entries('x.txt')", str(D / "reference")],
                               cwd=t, capture_output=True, text=True)
            self.assertIn("ValueError: too many values to unpack (expected 4", p.stderr)   # 3.13 是 (expected 4)，3.14 起多寫 got 5
            self.assertEqual(Path(t, "x.txt").read_text(encoding="utf-8"), "11/05,聚餐,600,跟小明, 小華\n")


if __name__ == "__main__":
    unittest.main()
