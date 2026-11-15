"""1-13〈list：一串帳目〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

新東西只有一個，只對寫了它的 checks.json 生效：
  - chaff assert 模式的 eval_once：assert 左右兩邊各算一次。remove_last(a) 這種會改 list 的呼叫，不會為了報「正確版算出來是多少」
    再被呼叫一次（不然報出來的是第二次 pop 的值，而且 a 又少一筆）。
第③圈的壞版本：m1 index_of_max 找對了位置、最後多一行 amounts.sort()（主角：只看交回的答案抓不到，要查完再比原本的 list）、
m2 remove_last 刪第一筆、m3 一樣大的交回最後面那一筆。ledger.py、sort.py 有 swap：把答案寫死的過不了。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l113"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-13"
D = COURSE / "lessons" / LID
IMP = "from entries import remove_last, index_of_max\n"
# 影片裡熊的第一版：只看交回的答案（index_of_max 傳的是直接寫的 list）→ 壞版本 1（多一行 sort）溜過去
BEAR_V1 = (IMP + "# 刪掉最後一筆：交回那一筆，list 少一筆\n"
           "a = [120, 85, 200]\nassert remove_last(a) == 200\nassert a == [120, 85]\n"
           "# 最大的一筆在第幾個位置（從 0 數）\n"
           "assert index_of_max([120, 300, 85]) == 1\nassert index_of_max([85, 120, 300]) == 2\n"
           "# 一樣大的，交回前面那一筆\nassert index_of_max([300, 85, 300]) == 0\n")
# 第二版：先放進 b，查完再比 b 還是不是原本的順序 → 三個全抓到
BEAR_V2 = BEAR_V1.replace("assert index_of_max([120, 300, 85]) == 1\n",
                          "b = [120, 300, 85]\nassert index_of_max(b) == 1\nassert b == [120, 300, 85]\n")


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
    write(L / "lessons" / LID / "checks_list.py", text)
    return ev(["r3"])


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


class Asserts(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_checks_catch_all_three(self):
        out = r3((D / "answers" / "checks_list.py").read_text(encoding="utf-8"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 12 行抓到")   # 查完以後 b 還是原本的順序
        self.assertEqual(part(out, "m2").note, "被第 6 行抓到")    # 交回的不是 200
        self.assertEqual(part(out, "m3").note, "被第 14 行抓到")   # 一樣大的交回前面那一筆
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_bear_v1_lets_the_sorting_version_slip(self):
        out = r3(BEAR_V1)
        self.assertTrue(part(out, "count").ok and part(out, "wheat").ok, [(r.id, r.detail) for r in out.results])
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [False, True, True])
        self.assertIn("查完最大的以後，原本的 list 還是原本的順序嗎？", part(out, "m1").detail)
        self.assertIn("你的檢查抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)

    def test_bear_v2_catches_all(self):
        out = r3(BEAR_V2)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 9 行抓到")

    def test_len_after_does_not_catch_the_sort(self):
        """思考站的 C：查完以後筆數一樣是 3，排好也還是 3 筆，抓不到壞版本 1。"""
        out = r3(BEAR_V1 + "c = [120, 300, 85]\nassert index_of_max(c) == 1\nassert len(c) == 3\n")
        self.assertFalse(part(out, "m1").ok)

    def test_removing_after_the_lookup_also_catches_the_sort(self):
        out = r3(BEAR_V1 + "c = [120, 300, 85]\nassert index_of_max(c) == 1\nassert remove_last(c) == 85\n")
        self.assertTrue(part(out, "m1").ok, part(out, "m1").detail)

    def test_eval_once_reports_the_first_call(self):
        """寫錯的 assert（以為刪的是第一筆）：報出正確版第一次交回的 200，不是再 pop 一次的 85。"""
        out = r3(IMP + "a = [120, 85, 200]\nassert remove_last(a) == 120\nassert a == [120, 85]\n"
                 "assert index_of_max([1, 9, 3]) == 1\nassert index_of_max([5, 5]) == 0\nassert index_of_max([7]) == 0\n")
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn("第 3 行：assert remove_last(a) == 120", r.detail)
        self.assertIn("正確版算出來是200", r.detail)
        self.assertNotIn("85", r.detail.split("\n")[1])
        self.assertNotIn("第 4 行", r.detail)   # 第一次呼叫以後 a 是 [120, 85]，第 4 行在正確版上成立

    def test_eval_once_list_value_is_a_snapshot(self):
        out = r3(IMP + "a = [120, 85, 200]\nassert a == [120, 85]\nassert remove_last(a) == 200\n"
                 "assert index_of_max([1, 9, 3]) == 1\nassert index_of_max([5, 5]) == 0\nassert index_of_max([7]) == 0\n")
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn("正確版算出來是[120, 85, 200]", r.detail)

    def test_start_file_needs_five(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("5", part(out, "count").detail)

    def test_eval_once_only_in_this_lesson(self):
        for lid in ("1-8", "1-12"):
            les = grader.load_lesson(lid, COURSE)
            self.assertFalse(any(c.get("eval_once") for c in les.checks), lid)
        les = grader.load_lesson(LID, COURSE)
        self.assertTrue(next(c for c in les.checks if c["id"] == "r3")["eval_once"])


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_index_and_sort_quiz(self):
        answer("index.txt", ["85", "150", "A", "85"])
        answer("sort_quiz.txt", ["A", "C", "B"])
        out = ev(["index", "sortq"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_index_from_one_is_wrong(self):
        answer("index.txt", ["120", "95", "B", "60"])
        out = ev(["index"])
        self.assertEqual([r.ok for r in out.results], [False, False, False, False])
        self.assertIn("索引從 0 開始數", out.results[0].detail)

    def test_sort_quiz_two_letters_is_not_a_choice(self):
        answer("sort_quiz.txt", ["A", "B 或 C", "B"])
        out = ev(["sortq"])
        self.assertFalse(out.results[1].ok)
        self.assertIn("只能選一個", out.results[1].detail)


class Programs(unittest.TestCase):
    def setUp(self):
        start()

    def test_references_pass_and_starts_do_not(self):
        ids = ["ledger-1", "ledger-2", "fix", "sort-1", "sort-2"]
        out = ev(ids)
        self.assertFalse(any(r.ok for r in out.results))
        for f in ("ledger.py", "fix.py", "sort.py"):
            shutil.copy(D / "reference" / f, L / "lessons" / LID / f)
        out = ev(ids)
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_hardcoded_ledger_fails_the_swap(self):
        write(L / "lessons" / LID / "ledger.py", 'amounts = [120, 85, 200, 95]\namounts.append(150)\n'
              'print("一共 5 筆，合計 650 元")\nprint("第一筆 120 元，最後一筆 150 元")\n')
        out = ev(["ledger-1", "ledger-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])
        self.assertIn("換成 [100, 160, 90]", out.results[1].detail)

    def test_fstring_and_halfwidth_comma_are_fine(self):
        write(L / "lessons" / LID / "ledger.py", 'amounts = [120, 85, 200, 95]\namounts.append(150)\n'
              'print(f"一共{len(amounts)}筆,合計{sum(amounts)}元")\nprint(f"第一筆{amounts[0]}元，最後一筆{amounts[-1]}元")\n')
        out = ev(["ledger-1", "ledger-2"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_index_from_one(self):
        src = (D / "reference" / "ledger.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "ledger.py", src.replace("amounts[0]", "amounts[1]"))
        out = ev(["ledger-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("第一筆 85 元", out.results[0].detail)

    def test_sort_in_place_fails(self):
        write(L / "lessons" / LID / "sort.py", 'amounts = [120, 85, 200, 95]\namounts.sort()\n'
              'print("由小到大", amounts)\nprint("原本的順序", amounts)\n')
        out = ev(["sort-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("sorted(amounts)", out.results[0].detail)

    def test_sorted_result_of_sort_is_none(self):
        write(L / "lessons" / LID / "sort.py", 'amounts = [120, 85, 200, 95]\nb = amounts.sort()\n'
              'print("由小到大", b)\nprint("原本的順序", amounts)\n')
        out = ev(["sort-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("None", out.results[0].detail)

    def test_remove_with_an_index_crashes(self):
        src = (D / "reference" / "fix.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "fix.py", src.replace("remove(85)", "remove(1)"))
        out = ev(["fix"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("ValueError", out.results[0].detail)


if __name__ == "__main__":
    unittest.main()
