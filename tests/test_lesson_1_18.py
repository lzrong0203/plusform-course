"""1-18〈函式（上）：def、參數、return〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 新加 type func_shape（只對寫了它的 checks.json 生效）：只看程式的樣子——有沒有 def 那個名字、docstring 有沒有寫輸入／輸出／例子
（例子要寫到一次呼叫）、有沒有用 return 交回一個值（只 print 不 return，外面拿到的是 None）。其他用到的是前幾課已有的：
answers（strict_choice）、call（直接呼叫學員的函式，含空的 list；交回 None 時提示「常常是用了 print」）、run 的 runs＋swap、chaff 的 assert 模式。
第③圈：學員的 assert 拿去跑課程的正確版和 3 個 AI 寫錯的版本（m1 算成有幾筆、m2 同一類沒加起來、m3 空的 list 交回 None）；
起點檔的範例（同一類兩筆加起來）抓到 m1、m2，m3 只有交空的 list 的那一條抓得到（影片第③圈的思考站）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l118"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-18"
D = COURSE / "lessons" / LID
IMP = "from by_category import by_category\n"
BEAR = (IMP + "# 同一類的兩筆要加起來\nassert by_category([(\"餐\", 120), (\"餐\", 85)]) == {\"餐\": 205}\n"
        "# 兩類各自加\nassert by_category([(\"餐\", 120), (\"車\", 30)]) == {\"餐\": 120, \"車\": 30}\n"
        "# 空的 list：交回空的 dict\nassert by_category([]) == {}\n")   # 影片裡熊寫的三條
DOC = ('    """各分類的小計。\n\n    輸入：entries 是一串 (分類, 金額)，可以是空的。\n'
       '    輸出：dict，分類 → 合計金額；空的 list 交回 {}。\n'
       '    例子：by_category([("餐", 120), ("餐", 85)]) 是 {"餐": 205}\n    """\n')
BODY = "    result = {}\n    for kind, amount in entries:\n        result[kind] = result.get(kind, 0) + amount\n    return result\n"


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
    write(mine("checks_by_category.py"), text)
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


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_predict_and_names(self):
        answer("predict.txt", ["B", "C", "A"])
        answer("names_quiz.txt", ["B", "A", "B", "C"])
        out = ev(["predict", "names"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_common_mistakes(self):
        """以為 print 出來的就是交回來的（10 和 10）、以為函式裡改不到外面的 list、以為 items = [] 會清空外面的。"""
        answer("predict.txt", ["A", "A", "B"])
        answer("names_quiz.txt", ["A", "B", "A", "A"])
        out = ev(["predict", "names"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_two_letters_is_not_a_choice(self):
        answer("predict.txt", ["B 或 C", "C", "A"])
        out = ev(["predict"])
        self.assertFalse(out.results[0].ok)


class Total(unittest.TestCase):
    IDS = ["total-def", "total-1", "total-2", "total-3", "total-run"]

    def setUp(self):
        start()

    def test_start_fails_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertFalse(part(out, "total-def").ok)
        self.assertIn("找不到 def total", part(out, "total-def").detail)
        self.assertTrue(part(out, "total-run").ok)   # 起點檔本來就印得對（還沒包成函式），靠 def 和 call 擋
        shutil.copy(D / "reference" / "total.py", mine("total.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_print_instead_of_return(self):
        """果凍兔的寫法：函式裡 print、沒有 return。func_shape 直接說，call 拿到 None 也提示。"""
        src = (D / "reference" / "total.py").read_text(encoding="utf-8").replace("    return s\n", "    print(s)\n")
        write(mine("total.py"), src)
        out = ev(self.IDS)
        self.assertFalse(part(out, "total-def").ok)
        self.assertIn("print 只會印在終端機", part(out, "total-def").detail)
        self.assertFalse(part(out, "total-1").ok)
        self.assertIn("常常是用了 print", part(out, "total-1").detail)
        self.assertFalse(part(out, "total-run").ok)

    def test_empty_list_needs_s_before_the_loop(self):
        write(mine("total.py"), "def total(amounts):\n    for a in amounts:\n        s = 0\n        s = s + a\n    return a\n\n"
              "nov = [120, 85, 300]\ndec = [65, 200]\nprint(\"11 月合計\", total(nov), \"元\")\nprint(\"12 月合計\", total(dec), \"元\")\n")
        out = ev(["total-1", "total-3"])
        self.assertEqual([r.ok for r in out.results], [False, False])

    def test_hardcoded_total_fails_the_swap(self):
        write(mine("total.py"), "def total(amounts):\n    s = 0\n    for a in amounts:\n        s = s + a\n    return s\n\n"
              "nov = [120, 85, 300]\ndec = [65, 200]\nprint(\"11 月合計\", 505, \"元\")\nprint(\"12 月合計\", total(dec), \"元\")\n")
        out = ev(["total-run"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("[10, 20]", out.results[0].detail)

    def test_sum_inside_also_passes(self):
        write(mine("total.py"), "def total(amounts):\n    return sum(amounts)\n\n"
              "nov = [120, 85, 300]\ndec = [65, 200]\nprint(\"11 月合計\", total(nov), \"元\")\nprint(\"12 月合計\", total(dec), \"元\")\n")
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class Add(unittest.TestCase):
    IDS = ["add-def", "add-1", "add-2"]

    def setUp(self):
        start()

    def test_start_fails_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        shutil.copy(D / "reference" / "add.py", mine("add.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_new_box_inside_does_not_change_outside(self):
        """函式裡 book = book + [amount]：只把函式裡的名牌換到新的盒子，外面的 nov 不變。"""
        src = (D / "reference" / "add.py").read_text(encoding="utf-8").replace("    book.append(amount)\n", "    book = book + [amount]\n")
        write(mine("add.py"), src)
        out = ev(["add-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("[120, 85]", out.results[0].detail)

    def test_hardcoded_nov_fails_the_swap(self):
        """函式裡寫死 nov.append：原本的跑起來剛好對，換成交 other 進去就錯（other 沒變、nov 多一筆）。"""
        src = (D / "reference" / "add.py").read_text(encoding="utf-8").replace("    book.append(amount)\n", "    nov.append(amount)\n")
        write(mine("add.py"), src)
        out = ev(["add-1", "add-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])
        self.assertIn("[10]", out.results[1].detail)


class ByCategory(unittest.TestCase):
    IDS = ["doc", "cat-1", "cat-2", "cat-3"]

    def setUp(self):
        start()

    def test_start_fails_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        self.assertIn("「輸入：」後面還空着", part(out, "doc").detail)
        shutil.copy(D / "reference" / "by_category.py", mine("by_category.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_docstring_only_returns_none(self):
        """只寫了 docstring、還沒有函式內容：docstring 那一題過不了 return，呼叫拿到 None。"""
        write(mine("by_category.py"), "def by_category(entries):\n" + DOC)
        out = ev(self.IDS)
        self.assertFalse(part(out, "doc").ok)
        self.assertIn("沒有 return", part(out, "doc").detail)
        self.assertFalse(part(out, "cat-2").ok)
        self.assertIn("回傳 None", part(out, "cat-2").detail)

    def test_ai_body_after_docstring_passes(self):
        write(mine("by_category.py"), "def by_category(entries):\n" + DOC + BODY)
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_no_docstring(self):
        write(mine("by_category.py"), "def by_category(entries):\n" + BODY)
        out = ev(["doc"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("還沒有 docstring", out.results[0].detail)

    def test_example_must_be_a_call(self):
        doc = DOC.replace('例子：by_category([("餐", 120), ("餐", 85)]) 是 {"餐": 205}', "例子：午餐和晚餐加起來")
        write(mine("by_category.py"), "def by_category(entries):\n" + doc + BODY)
        out = ev(["doc"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("要寫一次真的呼叫", out.results[0].detail)

    def test_missing_label(self):
        doc = DOC.replace("    輸出：dict，分類 → 合計金額；空的 list 交回 {}。\n", "")
        write(mine("by_category.py"), "def by_category(entries):\n" + doc + BODY)
        out = ev(["doc"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("找不到「輸出：」", out.results[0].detail)

    def test_halfwidth_colon_is_fine(self):
        write(mine("by_category.py"), "def by_category(entries):\n" + DOC.replace("：", ":") + BODY)
        self.assertTrue(ev(["doc"]).results[0].ok)

    def test_empty_list_returning_none_is_caught_by_the_course_tests(self):
        body = "    if len(entries) == 0:\n        return\n" + BODY
        write(mine("by_category.py"), "def by_category(entries):\n" + DOC + body)
        out = ev(self.IDS)
        self.assertEqual([part(out, k).ok for k in self.IDS], [True, True, False, True])


class Asserts(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_checks_catch_all_three(self):
        out = r3((D / "answers" / "checks_by_category.py").read_text(encoding="utf-8"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_bear_three_lines_catch_all_three(self):
        out = r3(BEAR)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_start_example_misses_the_empty_list_version(self):
        """起點檔的範例只有一條（同一類兩筆加起來）：m1、m2 抓到，m3（空的 list 交回 None）溜過去；條數也不夠。
        再補兩條「有資料」的（沒有空的 list）：寫滿 3 條，提示就指出 m3 要交空的 list 進去。"""
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, True, False])
        src = mine("checks_by_category.py").read_text(encoding="utf-8")
        out = r3(src + "assert by_category([(\"車\", 30)]) == {\"車\": 30}\nassert by_category([(\"餐\", 120), (\"車\", 30)]) == {\"餐\": 120, \"車\": 30}\n")
        self.assertTrue(part(out, "count").ok and part(out, "wheat").ok)
        self.assertFalse(part(out, "m3").ok)
        self.assertIn("空的 list", part(out, "m3").detail)

    def test_station_options(self):
        """思考站「哪一條，抓得到第三個版本？」：A 同一類兩筆、B 兩類各一筆都抓不到 m3，只有 C 空的 list 抓得到。"""
        a = r3(IMP + "assert by_category([(\"餐\", 120), (\"餐\", 85)]) == {\"餐\": 205}\n")
        b = r3(IMP + "assert by_category([(\"餐\", 120), (\"車\", 30)]) == {\"餐\": 120, \"車\": 30}\n")
        c = r3(IMP + "assert by_category([]) == {}\n")
        self.assertEqual([part(x, "m3").ok for x in (a, b, c)], [False, False, True])
        self.assertEqual([part(b, m).ok for m in ("m1", "m2")], [True, False])   # 兩類各一筆：沒有同一類的兩筆，蓋掉也看不出來

    def test_wrong_answer_fails_on_the_reference(self):
        out = r3(IMP + "assert by_category([]) == None\n")
        self.assertFalse(part(out, "wheat").ok)

    def test_green_runs_their_own_function(self):
        write(mine("checks_by_category.py"), BEAR)
        self.assertFalse(ev(["green"]).results[0].ok)   # 還只有 docstring：交回 None
        write(mine("by_category.py"), "def by_category(entries):\n" + DOC + BODY)
        out = ev(["green"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_frozen_version_passes_everything(self):
        """沒有 AI 帳號的：凍結版的函式內容抄進自己的 by_category.py（docstring 留自己寫的）。"""
        frozen = (D / "frozen" / "by_category.py").read_text(encoding="utf-8")
        body = frozen.split('    """\n', 1)[1]   # docstring 結束的那一行以下＝函式內容
        write(mine("by_category.py"), "def by_category(entries):\n" + DOC + body)
        write(mine("checks_by_category.py"), BEAR)
        out = ev(["doc", "cat-1", "cat-2", "cat-3", "green"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


if __name__ == "__main__":
    unittest.main()
