"""1-19〈函式（下）：預設值、關鍵字參數、範圍〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 的 call 加兩個只對寫了它的題目生效的欄位：kwargs（用關鍵字交的參數，light(1045, budget=1200)、over_limit(..., limit=100)）、
seq_as_list（交回的 tuple 跟 JSON 的 list 比，biggest 交回 ("書", 450)）。同一個檔案、同一個函式的 call 題在同一個程序裡照順序呼叫，
所以「第一次對、第二次就錯」（預設值 [] 的陷阱、結果存在函式外面的 list）抓得到。其他用到的是前幾課已有的：answers（strict_choice）、
func_shape、run、filled、chaff 的 assert 模式（eval_once：左右各算一次，報「交回什麼」時不會多呼叫一次）。
第③圈：學員的 assert 拿去跑課程的正確版和 3 個 AI 寫錯的版本（m1 結果存在函式外面、m2 門檻寫死 300、m3 都沒超過交回 None）；
影片裡熊的三條：m1、m2 被第二條抓到，m3 被第三條抓到（思考站「哪一條先失敗？」答案是第二條）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l119"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-19"
D = COURSE / "lessons" / LID
IMP = "from over_limit import over_limit\n"
A1 = "assert over_limit([120, 450, 85]) == [450]\n"
A2 = "assert over_limit([120, 450, 85], limit=100) == [120, 450]\n"
A3 = "assert over_limit([50, 80]) == []\n"
BEAR = IMP + "# 沒給 limit：用 300\n" + A1 + "# 用關鍵字給 limit\n" + A2 + "# 都沒超過：交回空的 list\n" + A3   # 影片裡熊寫的三條
DOC = ('    """挑出超過門檻的金額。\n\n    輸入：amounts 是一串金額；limit 是門檻，沒給就是 300\n'
       '    輸出：新的 list，照原本的順序；都沒超過交回 []\n'
       '    例子：over_limit([120, 450, 85]) 是 [450]\n    """\n')
BODY = "    result = []\n    for a in amounts:\n        if a > limit:\n            result.append(a)\n    return result\n"
HEAD = "def over_limit(amounts, limit=300):\n"


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
    write(mine("checks_over_limit.py"), text)
    return ev(["r3"])


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Scope(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("scope.txt", ["A", "B", "C", "B", "A"])
        out = ev(["scope"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_common_mistakes(self):
        """以為函式裡讀不到外面的、以為函式裡給值會改外面的、以為 count = count + 1 會用外面的 0、以為函式裡的名字外面拿得到、以為參數會改外面同名的。"""
        answer("scope.txt", ["B", "A", "A", "A", "B"])
        out = ev(["scope"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_answers_match_python(self):
        """題目裡的程式真的跑一次，答案跟 answers/scope.json 一致（錯誤訊息的題目答「出現錯誤訊息」）。"""
        import json
        key = json.loads((D / "answers" / "scope.json").read_text(encoding="utf-8"))
        blocks = (D / "start" / "scope.txt").read_text(encoding="utf-8").split("\n答：")[:-1]
        for blk, q in zip(blocks, key["questions"]):
            code = "\n".join(ln[4:] for ln in blk.split("題：")[-1].splitlines() if ln.startswith("#   ") and not ln.startswith("#   A.")
                             and not ln.startswith("#   B.") and not ln.startswith("#   C.")) + "\n"
            code = "\n".join(ln for ln in code.splitlines()) + "\n"
            import contextlib
            import io
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    exec(compile(code, "<q>", "exec"), {})
                got = " 和 ".join(buf.getvalue().split())
            except Exception:  # noqa: BLE001
                got = "出現錯誤訊息"
            self.assertEqual(q["choices"][q["accept"][0]], got, (q["id"], code))

    def test_two_letters_is_not_a_choice(self):
        answer("scope.txt", ["A 或 B", "B", "C", "B", "A"])
        out = ev(["scope"])
        self.assertFalse(out.results[0].ok)


class AddEntry(unittest.TestCase):
    IDS = ["add-def", "add-1", "add-2", "add-3", "add-run"]

    def setUp(self):
        start()

    def test_start_trap_is_caught_on_the_second_call(self):
        """起點檔（預設值 []）：check 載入檔案時最下面已經呼叫過兩次（共用同一個 list），所以沒給帳本的兩題都錯，
        報出來的是那一刻交回的（[120, 65, 120]），提示講預設值只做一次；有給帳本的那題對。"""
        out = ev(self.IDS)
        self.assertEqual([part(out, k).ok for k in self.IDS], [True, False, False, True, False])
        self.assertIn("預設值只在", part(out, "add-1").detail)
        self.assertIn("[120, 65, 120]", part(out, "add-1").detail)
        self.assertIn("[120, 65, 120, 65]", part(out, "add-2").detail)

    def test_reference_passes(self):
        shutil.copy(D / "reference" / "add_entry.py", mine("add_entry.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_always_new_book_ignores_the_given_book(self):
        """每次都做新的（不管有沒有交帳本進來）：沒給帳本的兩題對，有給帳本的那題錯。"""
        write(mine("add_entry.py"), "def add_entry(amount, book=None):\n    book = []\n    book.append(amount)\n    return book\n\n\n"
              "nov = add_entry(120)\ndec = add_entry(65)\nprint(nov, dec)\n")
        out = ev(["add-1", "add-2", "add-3"])
        self.assertEqual([r.ok for r in out.results], [True, True, False])

    def test_no_return(self):
        write(mine("add_entry.py"), "def add_entry(amount, book=None):\n    if book is None:\n        book = []\n    book.append(amount)\n\n\n"
              "nov = add_entry(120)\ndec = add_entry(65)\nprint(nov, dec)\n")
        out = ev(["add-def", "add-1"])
        self.assertFalse(part(out, "add-def").ok)
        self.assertIn("沒有 return", part(out, "add-def").detail)
        self.assertFalse(part(out, "add-1").ok)


class Split(unittest.TestCase):
    IDS = ["split-total", "split-cat", "split-big", "split-light1", "split-light2", "split-run"]

    def setUp(self):
        start()

    def test_start_fails_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        self.assertIn("回傳 None", part(out, "split-total").detail)
        shutil.copy(D / "reference" / "split.py", mine("split.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_report_long_prints_the_same(self):
        """起點檔的 report_long.py（不用改）跑出來的，就是 split-run 要的那 14 行。"""
        shutil.copy(D / "start" / "report_long.py", mine("split.py"))
        out = ev(["split-run"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_hardcoded_budget_fails_the_keyword_call(self):
        src = (D / "reference" / "split.py").read_text(encoding="utf-8").replace("ratio = s / budget", "ratio = s / 1000")
        write(mine("split.py"), src)
        out = ev(["split-light1", "split-light2", "split-run"])
        self.assertEqual([r.ok for r in out.results], [True, False, False])
        self.assertIn("budget=1200", out.results[1].detail)
        self.assertIn("ratio = s / budget", out.results[1].detail)

    def test_tuple_or_list_both_fine_for_biggest(self):
        src = (D / "reference" / "split.py").read_text(encoding="utf-8").replace("    return big\n", "    return [big[0], big[1]]\n")
        write(mine("split.py"), src)
        self.assertTrue(ev(["split-big"]).results[0].ok)


class Tutor(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_then_filled(self):
        out = ev(["tutor"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("「我踩到的錯：」後面還空着", out.results[0].detail)
        p = mine("tutor.md")
        txt = p.read_text(encoding="utf-8")
        for lab in ("我踩到的錯：", "家教問我的：", "我的回答：", "我出的題目：", "家教的回答：", "跑出來對不對："):
            txt = txt.replace(lab + "\n", lab + "寫了一些字\n", 1)
        p.write_text(txt, encoding="utf-8")
        out = ev(["tutor"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)


class OverLimit(unittest.TestCase):
    IDS = ["doc", "lim-1", "lim-2", "lim-3", "lim-4"]

    def setUp(self):
        start()

    def test_start_fails_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        self.assertIn("「輸入：」後面還空着", part(out, "doc").detail)
        shutil.copy(D / "reference" / "over_limit.py", mine("over_limit.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_global_result_is_right_first_then_wrong(self):
        """AI 把 result = [] 寫在函式外面：第一次呼叫對，第二次（同一個程序）就錯，提示講第一次對、第二次就錯。"""
        write(mine("over_limit.py"), "result = []\n\n\n" + HEAD + DOC + BODY.replace("    result = []\n", ""))
        out = ev(self.IDS)
        self.assertEqual([part(out, k).ok for k in self.IDS], [True, True, False, False, False])
        self.assertIn("第一次對、第二次就錯", part(out, "lim-2").detail)
        self.assertIn("[450, 120, 450]", part(out, "lim-2").detail)
        self.assertIn("limit=100", part(out, "lim-2").detail)

    def test_mutable_default_is_also_right_first_then_wrong(self):
        write(mine("over_limit.py"), "def over_limit(amounts, limit=300, result=[]):\n" + DOC + BODY.replace("    result = []\n", ""))
        out = ev(["lim-1", "lim-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])

    def test_docstring_only_returns_none(self):
        write(mine("over_limit.py"), HEAD + DOC)
        out = ev(self.IDS)
        self.assertFalse(part(out, "doc").ok)
        self.assertIn("沒有 return", part(out, "doc").detail)
        self.assertIn("回傳 None", part(out, "lim-1").detail)

    def test_ai_body_after_docstring_passes(self):
        write(mine("over_limit.py"), HEAD + DOC + BODY)
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class Asserts(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_checks_catch_all_three(self):
        out = r3((D / "answers" / "checks_over_limit.py").read_text(encoding="utf-8"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_start_example_alone_catches_nothing(self):
        """起點檔只有一條範例（呼叫一次）：三個壞版本都抓不到，條數也不夠。"""
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [False, False, False])

    def test_one_call_cannot_catch_the_global_version(self):
        """只呼叫一次（不管哪一條）：m1 都抓不到；同一條寫兩次就抓到（第二次呼叫）。"""
        for one in (A1, A2, A3):
            self.assertFalse(part(r3(IMP + one), "m1").ok, one)
        self.assertTrue(part(r3(IMP + A1 + A1), "m1").ok)

    def test_station_which_fails_first(self):
        """思考站「熊的三條 assert，哪一條先失敗？」：在 m1 上第一條成立、第二條就不成立（答案 B）。"""
        les = grader.load_lesson(LID, COURSE)
        spec = next(c for c in les.checks if c["id"] == "r3")
        write(mine("checks_over_limit.py"), BEAR)
        ctx = grader.Ctx(les, L, grader.Env(L))
        chk = grader.ChaffCheck(spec, ctx)
        res = chk.run_assert_version(D / "mutants" / "over_limit_m1.py", [])
        lines = sorted(res)
        self.assertEqual([res[k]["status"] for k in lines], ["pass", "fail", "fail"])
        self.assertEqual(res[lines[1]].get("got"), [450, 120, 450])   # eval_once：報出來的就是第二次呼叫交回的，不會多呼叫一次

    def test_bear_three_lines_catch_all_three(self):
        out = r3(BEAR)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_without_keyword_misses_hardcoded_300(self):
        out = r3(IMP + A1 + A3 + "assert over_limit([500, 320, 80]) == [500, 320]\n")
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, False, True])
        self.assertIn("limit=", part(out, "m2").detail)

    def test_without_nothing_over_misses_none_version(self):
        out = r3(IMP + A1 + A2 + "assert over_limit([500, 320, 80]) == [500, 320]\n")
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, True, False])
        self.assertIn("空的 list", part(out, "m3").detail)

    def test_wrong_answer_fails_on_the_reference(self):
        out = r3(IMP + "assert over_limit([50, 80]) == None\n" + A1 + A2)
        self.assertFalse(part(out, "wheat").ok)

    def test_green_runs_their_own_function(self):
        write(mine("checks_over_limit.py"), BEAR)
        self.assertFalse(ev(["green"]).results[0].ok)   # 還只有 docstring：交回 None
        write(mine("over_limit.py"), HEAD + DOC + BODY)
        out = ev(["green"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_frozen_version_passes_everything(self):
        """沒有 AI 帳號的：凍結版的函式內容抄進自己的 over_limit.py（docstring 留自己寫的）。"""
        frozen = (D / "frozen" / "over_limit.py").read_text(encoding="utf-8")
        body = frozen.split('    """\n', 1)[1]   # docstring 結束的那一行以下＝函式內容
        write(mine("over_limit.py"), HEAD + DOC + body)
        write(mine("checks_over_limit.py"), BEAR)
        out = ev(["doc", "lim-1", "lim-2", "lim-3", "lim-4", "green"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


if __name__ == "__main__":
    unittest.main()
