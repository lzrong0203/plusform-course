"""1-20〈看懂 AI 常用的寫法（下）：型別提示、lambda、sorted 的 key、any／all、*args〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 加的東西（只對寫了它的題目生效）：run 的 ast_require 多兩種——keyfunc（name = sorted(…, key=某個用 def 寫的函式)，不能用 lambda、不能直接抄 AI 的結果）、
flagloop（先給 True／False，再在 for 迴圈裡改，不能用 any／all）；func_shape 加 annotated（每個參數和交回的值都寫了型別提示）。
其他用到的是前幾課已有的：answers（strict_choice）、run（swap、loose）、filled、func_shape、call（seq_as_list：交回 list 裡的 tuple 跟 JSON 的 list 比）、chaff 的 assert 模式。
第③圈：學員的 assert 拿去跑課程的正確版和 3 個 AI 寫錯的版本（m1 key 方向寫反、m2 沒有先依分類加總、m3 沒有只留前三類）；
影片裡熊的三條：第一條（只有一類）只抓到 m2，第二條（四類、同一類好幾筆、金額有大有小）三個都抓到，第三條（空的 list）一個都抓不到
（思考站「哪一條抓得到 key 方向寫反的版本？」答案是第二條）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l120"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-20"
D = COURSE / "lessons" / LID
IMP = "from top3 import top3\n"
A1 = 'assert top3([("餐", 120), ("餐", 85)]) == [("餐", 205)]\n'
A2 = 'assert top3([("餐", 120), ("書", 450), ("餐", 300), ("車", 30), ("衣", 60)]) == [("書", 450), ("餐", 420), ("衣", 60)]\n'
A3 = "assert top3([]) == []\n"
BEAR = IMP + "# 同一類的兩筆要加起來\n" + A1 + "# 四類，同一類好幾筆、金額有大有小\n" + A2 + "# 空的 list：交回空的 list\n" + A3   # 影片裡熊寫的三條
HEAD = "def top3(entries: list[tuple[str, int]]) -> list[tuple[str, int]]:\n"
DOC = ('    """依分類加總，排出花費最大的前三類。\n\n'
       '    輸入：entries，一串 (分類, 金額)，同一類可以有好幾筆，可以是空的\n'
       '    輸出：list，每一筆是 (分類, 合計)，合計大的在前，最多三類；空的交回 []\n'
       '    例子：top3([("餐", 120), ("餐", 85)]) 是 [("餐", 205)]\n    """\n')
BODY = ("    totals = {}\n    for cat, amount in entries:\n        totals[cat] = totals.get(cat, 0) + amount\n"
        "    return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:3]\n")


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
    write(mine("checks_top3.py"), text)
    return ev(["r3"])


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def quiz_blocks(name: str) -> list[str]:
    """作答檔每一題的程式（「#   」開頭、不是選項的那幾行）。"""
    blocks = (D / "start" / name).read_text(encoding="utf-8").split("\n答：")[:-1]
    out = []
    for blk in blocks:
        body = blk.split("題：")[-1].splitlines()
        code = [ln[4:] for ln in body if ln.startswith("#   ") and not ln.startswith(("#   A.", "#   B.", "#   C."))]
        out.append("\n".join(code) + "\n")
    return out


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Predict(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("predict.txt", ["B", "A", "C"])
        out = ev(["predict"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_common_mistakes(self):
        """以為型別提示會擋下 85.0、以為 reverse=True 會把一樣大的也倒過來、以為 *items 一個都不交會出錯。"""
        answer("predict.txt", ["C", "B", "B"])
        out = ev(["predict"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_answers_match_python(self):
        """題目裡的程式真的跑一次，跟 answers/predict.json 的答案一致（第 2 題看前兩行）。"""
        key = json.loads((D / "answers" / "predict.json").read_text(encoding="utf-8"))
        codes = quiz_blocks("predict.txt")
        got = []
        for code in codes:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "<q>", "exec"), {})
            got.append(buf.getvalue().splitlines())
        self.assertEqual(got[0], ["42.0"])
        self.assertEqual(got[1][:2], ["餐 120", "書 120"])
        self.assertEqual(got[2], ["2 0"])
        want = [key["questions"][0]["choices"]["B"], key["questions"][1]["choices"]["A"], key["questions"][2]["choices"]["C"]]
        self.assertEqual(want, ["42.0", "餐 120 和 書 120", "2 0"])
        self.assertEqual([q["accept"] for q in key["questions"]], [["B"], ["A"], ["C"]])

    def test_two_letters_is_not_a_choice(self):
        answer("predict.txt", ["A 或 B", "A", "C"])
        out = ev(["predict"])
        self.assertFalse(out.results[0].ok)


class Plain(unittest.TestCase):
    IDS = ["plain-1", "plain-2"]

    def setUp(self):
        start()

    def test_start_fails_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        shutil.copy(D / "reference" / "plain.py", mine("plain.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def _with(self, old: str, new: str) -> str:
        src = (D / "reference" / "plain.py").read_text(encoding="utf-8")
        assert old in src, old
        return src.replace(old, new)

    def test_lambda_left_in_is_refused(self):
        """還是用 lambda（結果一樣，五個 True）：keyfunc 擋下來。"""
        write(mine("plain.py"), self._with("newest2 = sorted(entries, key=date_of, reverse=True)", "newest2 = sorted(entries, key=lambda e: e[0], reverse=True)"))
        out = ev(["plain-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("newest2 要用 sorted 排", out.results[0].detail)

    def test_copying_ai_result_is_refused(self):
        write(mine("plain.py"), self._with("top2b = sorted(entries, key=amount_of, reverse=True)[:2]", "top2b = top2"))
        out = ev(["plain-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("top2b 要用 sorted 排", out.results[0].detail)

    def test_any_left_in_is_refused(self):
        src = self._with("has_big2 = False\nfor e in entries:\n    if e[2] >= 300:\n        has_big2 = True\n", "has_big2 = any(e[2] >= 300 for e in entries)\n")
        write(mine("plain.py"), src)
        out = ev(["plain-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("has_big2 要改回迴圈", out.results[0].detail)

    def test_forgot_reverse_prints_false(self):
        write(mine("plain.py"), self._with("newest2 = sorted(entries, key=date_of, reverse=True)\nassert newest2 == newest\n", "newest2 = sorted(entries, key=date_of)\n"))
        out = ev(["plain-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("True False True True True", out.results[0].detail)

    def test_hardcoded_flag_fails_on_swapped_data(self):
        """has_big2 寫成迴圈裡一律改 True（原本的資料剛好對）：換資料（沒有一筆 >= 300）就印出 False。"""
        write(mine("plain.py"), self._with("    if e[2] >= 300:\n        has_big2 = True\n", "    has_big2 = True\n"))
        out = ev(self.IDS)
        self.assertEqual([r.ok for r in out.results], [True, False])

    def test_tuple_key_or_def_both_fine(self):
        """key 交的函式名字隨便取都可以（不一定叫 date_of）。"""
        src = self._with("def date_of(e):\n    return e[0]\n", "def get_date(e):\n    return e[0]\n").replace("key=date_of", "key=get_date")
        write(mine("plain.py"), src)
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class Sort2(unittest.TestCase):
    IDS = ["sort-1", "sort-2"]

    def setUp(self):
        start()

    def test_start_fails_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertFalse(any(r.ok for r in out.results))
        shutil.copy(D / "reference" / "sort2.py", mine("sort2.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def _result(self, code: str) -> grader.Outcome:
        src = (D / "start" / "sort2.py").read_text(encoding="utf-8").replace("result = entries   # 改這一行（可以寫成好幾行）", code)
        write(mine("sort2.py"), src)
        return ev(self.IDS)

    def test_amount_only_keeps_original_order(self):
        """只照金額排一次：一樣大的照原本的順序（11/03 在 11/02 前面），不是照日期。"""
        out = self._result("result = sorted(entries, key=lambda e: e[2])")
        self.assertEqual([r.ok for r in out.results], [False, False])

    def test_wrong_order_of_two_sorts(self):
        out = self._result("by_amount = sorted(entries, key=lambda e: e[2])\nresult = sorted(by_amount, key=lambda e: e[0])")
        self.assertEqual([r.ok for r in out.results], [False, False])

    def test_tuple_key_is_also_fine(self):
        out = self._result("result = sorted(entries, key=lambda e: (e[2], e[0]))")
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class Translate(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_and_wrong(self):
        answer("translate.txt", ["A", "B", "C", "B"])
        out = ev(["translate"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        answer("translate.txt", ["B", "A", "A", "A"])   # 以為型別提示會檢查、以為 e 是第三筆、把 all 當 any、以為 *amounts 要交 list
        out = ev(["translate"])
        self.assertFalse(any(r.ok for r in out.results))

    def test_four_questions(self):
        self.assertEqual(len(quiz_blocks("translate.txt")), 4)


class Tutor(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_then_filled(self):
        out = ev(["tutor"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("「家教問我的：」後面還空着", out.results[0].detail)
        p = mine("tutor.md")
        txt = p.read_text(encoding="utf-8")
        for lab in ("家教問我的：", "我一開始的回答：", "家教怎麼說：", "我加 print 跑出來的："):
            txt = txt.replace(lab + "\n", lab + "寫了一些字\n", 1)
        p.write_text(txt, encoding="utf-8")
        out = ev(["tutor"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)


class Top3(unittest.TestCase):
    IDS = ["doc", "top-1", "top-2", "top-3"]

    def setUp(self):
        start()

    def test_start_fails_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        self.assertIn("「輸入：」後面還空着", part(out, "doc").detail)
        shutil.copy(D / "reference" / "top3.py", mine("top3.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_hints_removed_is_refused(self):
        write(mine("top3.py"), "def top3(entries):\n" + DOC + BODY)
        out = ev(["doc"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("型別提示還沒寫完", out.results[0].detail)
        self.assertIn("entries", out.results[0].detail)
        write(mine("top3.py"), "def top3(entries: list[tuple[str, int]]):\n" + DOC + BODY)
        out = ev(["doc"])
        self.assertIn("-> 型別", out.results[0].detail)

    def test_each_mutant_fails_some_call(self):
        for m, want in (("m1", [True, False, False, True]), ("m2", [True, False, False, True]), ("m3", [True, False, True, True])):
            src = (D / "mutants" / f"top3_{m}.py").read_text(encoding="utf-8")
            write(mine("top3.py"), src)
            out = ev(self.IDS)
            self.assertEqual([part(out, k).ok for k in self.IDS], want, m)

    def test_ai_body_after_docstring_passes(self):
        write(mine("top3.py"), HEAD + DOC + BODY)
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_docstring_only_returns_none(self):
        write(mine("top3.py"), HEAD + DOC)
        out = ev(self.IDS)
        self.assertFalse(part(out, "doc").ok)
        self.assertIn("沒有 return", part(out, "doc").detail)
        self.assertIn("回傳 None", part(out, "top-1").detail)


class Asserts(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_checks_catch_all_three(self):
        out = r3((D / "answers" / "checks_top3.py").read_text(encoding="utf-8"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_start_example_alone_catches_only_m2(self):
        """起點檔只有一條範例（只有一類）：只抓到沒先加總的 m2，條數也不夠。"""
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [False, True, False])

    def test_station_which_catches_reversed_key(self):
        """思考站「熊的三條，哪一條抓得到 key 方向寫反的版本？」：在 m1 上第一、三條成立，只有第二條不成立（答案 B）。"""
        les = grader.load_lesson(LID, COURSE)
        spec = next(c for c in les.checks if c["id"] == "r3")
        write(mine("checks_top3.py"), BEAR)
        ctx = grader.Ctx(les, L, grader.Env(L))
        chk = grader.ChaffCheck(spec, ctx)
        res = chk.run_assert_version(D / "mutants" / "top3_m1.py", [])
        lines = sorted(res)
        self.assertEqual([res[k]["status"] for k in lines], ["pass", "fail", "pass"])

    def test_one_category_only_cannot_catch_reversed_key(self):
        out = r3(IMP + A1 + 'assert top3([("車", 30), ("車", 60)]) == [("車", 90)]\n' + A3)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [False, True, False])
        self.assertIn("兩類以上", part(out, "m1").detail)

    def test_bear_three_lines_catch_all_three(self):
        out = r3(BEAR)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_three_categories_miss_the_top3_limit(self):
        """兩類以上抓得到 m1，可是不到四類就抓不到「沒有只留前三類」的 m3。"""
        out = r3(IMP + A1 + 'assert top3([("餐", 120), ("書", 450), ("餐", 300), ("車", 30)]) == [("書", 450), ("餐", 420), ("車", 30)]\n' + A3)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, True, False])
        self.assertIn("多於三類", part(out, "m3").detail)

    def test_wrong_answer_fails_on_the_reference(self):
        out = r3(IMP + A1 + 'assert top3([("餐", 120), ("書", 450)]) == [("餐", 120), ("書", 450)]\n' + A3)
        self.assertFalse(part(out, "wheat").ok)

    def test_green_runs_their_own_function(self):
        write(mine("checks_top3.py"), BEAR)
        self.assertFalse(ev(["green"]).results[0].ok)   # 還只有 docstring：交回 None
        write(mine("top3.py"), HEAD + DOC + BODY)
        out = ev(["green"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_frozen_version_passes_everything(self):
        """沒有 AI 帳號的：凍結版的函式內容抄進自己的 top3.py（docstring 留自己寫的）。"""
        frozen = (D / "frozen" / "top3.py").read_text(encoding="utf-8")
        body = frozen.split('    """\n', 1)[1]   # docstring 結束的那一行以下＝函式內容
        write(mine("top3.py"), HEAD + DOC + body)
        write(mine("checks_top3.py"), BEAR)
        out = ev(["doc", "top-1", "top-2", "top-3", "green", "r3"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class Deep(unittest.TestCase):
    def test_optional_deep_sum(self):
        """選做的 deep.py（check 不檢查）：跑出來是 550，補充.md 寫的答案也是 550。"""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile((D / "start" / "deep.py").read_text(encoding="utf-8"), "<deep>", "exec"), {})
        self.assertEqual(buf.getvalue().strip(), "550")


if __name__ == "__main__":
    unittest.main()
