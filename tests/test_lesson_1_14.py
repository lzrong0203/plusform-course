"""1-14〈tuple、set 與拆包〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

這一課沒有改 grader／runner，用到的都是前幾課已有的：answers（strict_choice、每題自己的 choices）、run 的 swap（1-C1）、chaff 的 assert 模式（1-8）。
第③圈的壞版本：m1 少了 sorted、直接交回 set（主角：只用 in、not in、len 抓不到，要拿整串排好的 list 用兩個等號比）、
m2 交集寫成聯集、m3 沒有用 set、同一個分類記了好幾筆就重複出現。record.py、swap.py、kinds.py 有 swap：把答案寫死的過不了。
set 的順序每次執行可能不一樣：m1 交回的是 set，跟 list 用兩個等號比一定不一樣，所以抓不抓得到跟順序無關（這裡每個測試跑兩次確認結果一樣）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l114"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-14"
D = COURSE / "lessons" / LID
IMP = "from months import both_months\n"
DATA = 'nov = ["餐飲", "交通", "餐飲", "娛樂"]\ndec = ["交通", "醫療", "餐飲", "交通"]\n'
# 影片裡熊的第一版：只用 in、not in、len → 壞版本 1（少了 sorted，交回 set）溜過去
BEAR_V1 = (IMP + DATA + "r = both_months(nov, dec)\n"
           "# 兩個月都有的分類，要在裡面\nassert \"交通\" in r\nassert \"餐飲\" in r\n"
           "# 只有一個月有的，不能放進去\nassert \"娛樂\" not in r\nassert \"醫療\" not in r\n"
           "# 每個分類只出現一次\nassert len(r) == 2\n")
# 第二版：補一條比整串、連順序一起比 → 三個全抓到
BEAR_V2 = BEAR_V1 + "# 排好序：比整串\nassert r == [\"交通\", \"餐飲\"]\n"


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
    write(L / "lessons" / LID / "checks_months.py", text)
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
        out = r3((D / "answers" / "checks_months.py").read_text(encoding="utf-8"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 7 行抓到")    # 比整串：set 跟 list 一定不一樣
        self.assertEqual(part(out, "m2").note, "被第 7 行抓到")    # 聯集多了娛樂、醫療，整串就不一樣
        self.assertEqual(part(out, "m3").note, "被第 7 行抓到")    # 餐飲 在 11 月記了兩筆 → 重複
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_bear_v1_lets_the_set_version_slip(self):
        for _ in range(2):   # set 的順序每次執行可能不一樣：結果要一樣
            out = r3(BEAR_V1)
            self.assertTrue(part(out, "count").ok and part(out, "wheat").ok, [(r.id, r.detail) for r in out.results])
            self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [False, True, True])
            self.assertIn("需求說排好序：交回的是排好的 list 嗎？", part(out, "m1").detail)
            self.assertIn("你的檢查抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)

    def test_bear_v2_catches_all(self):
        for _ in range(2):
            out = r3(BEAR_V2)
            self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
            self.assertEqual(part(out, "m1").note, "被第 14 行抓到")

    def test_station_options_a_and_c_do_not_catch_the_set(self):
        """思考站的 A（len == 2）、C（in）都看不出有沒有排好、是不是 list，抓不到壞版本 1。"""
        for extra in ("assert len(both_months(nov, dec)) == 2\n", "assert \"餐飲\" in both_months(nov, dec)\n"):
            out = r3(BEAR_V1 + extra)
            self.assertFalse(part(out, "m1").ok, extra)

    def test_sorted_around_the_call_hides_the_set(self):
        """自己先 sorted 再比，壞版本 1 交回的 set 被排好了，一樣溜過去（README 提示：要直接比交回的）。"""
        out = r3(BEAR_V1 + "assert sorted(r) == [\"交通\", \"餐飲\"]\n")
        self.assertFalse(part(out, "m1").ok)

    def test_comparing_with_a_set_fails_on_the_reference(self):
        """拿大括號的 set 比：正確版交回 list，這一條在正確版上不成立，報出正確版交回的 list。"""
        out = r3(BEAR_V1 + "assert r == {\"交通\", \"餐飲\"}\n")
        w = part(out, "wheat")
        self.assertFalse(w.ok)
        self.assertIn("['交通', '餐飲']", w.detail)

    def test_wrong_order_fails_on_the_reference(self):
        out = r3(BEAR_V1 + "assert r == [\"餐飲\", \"交通\"]\n")
        self.assertFalse(part(out, "wheat").ok)

    def test_duplicates_case_catches_m3_only_with_repeats(self):
        """不重複的資料抓不到壞版本 3：要有同一個分類記了好幾筆。"""
        once = IMP + 'r = both_months(["餐飲", "交通"], ["交通", "醫療"])\nassert r == ["交通"]\n' \
               'assert "醫療" not in r\nassert "餐飲" not in r\nassert len(r) == 1\nassert "交通" in r\n'
        out = r3(once)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, True, False])

    def test_start_file_needs_five(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("5", part(out, "count").detail)


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_predict_and_set_quiz(self):
        answer("predict.txt", ["午餐", "B", "A", "B"])
        answer("set_quiz.txt", ["C", "B", "A", "B"])
        out = ev(["predict", "setq"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_predict_quotes_are_fine(self):
        answer("predict.txt", ['"午餐"', "b", "a", "B"])
        out = ev(["predict"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_predict_common_mistakes(self):
        answer("predict.txt", ["11/03", "A", "B", "A"])
        out = ev(["predict"])
        self.assertEqual([r.ok for r in out.results], [False, False, False, False])
        self.assertIn("從 0 開始數", out.results[0].detail)

    def test_set_quiz_two_letters_is_not_a_choice(self):
        answer("set_quiz.txt", ["A 或 C", "B", "A", "B"])
        out = ev(["setq"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("只能選一個", out.results[0].detail)


class Programs(unittest.TestCase):
    def setUp(self):
        start()

    def test_references_pass_and_starts_do_not(self):
        ids = ["record-1", "record-2", "swap-1", "swap-2", "kinds-1", "kinds-2"]
        out = ev(ids)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        for f in ("record.py", "swap.py", "kinds.py"):
            shutil.copy(D / "reference" / f, L / "lessons" / LID / f)
        out = ev(ids)
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_indexing_instead_of_unpacking_is_fine(self):
        write(L / "lessons" / LID / "record.py", 'record = ("11/03", "午餐", 120)\nprint(record[0], record[1], record[2], "元")\n')
        out = ev(["record-1", "record-2"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_hardcoded_record_fails_the_swap(self):
        write(L / "lessons" / LID / "record.py", 'record = ("11/03", "午餐", 120)\nprint("11/03 午餐 120 元")\n')
        out = ev(["record-1", "record-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])
        self.assertIn("電影", out.results[1].detail)

    def test_unpack_count_mismatch_crashes(self):
        write(L / "lessons" / LID / "record.py", 'record = ("11/03", "午餐", 120)\ndate, item = record\nprint(date, item, "元")\n')
        out = ev(["record-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("ValueError", out.results[0].detail)

    def test_two_line_swap_prints_five_five(self):
        write(L / "lessons" / LID / "swap.py", "a = 3\nb = 5\na = b\nb = a\nprint(a, b)\n")
        out = ev(["swap-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("5 5", out.results[0].detail)
        self.assertIn("a, b = b, a", out.results[0].detail)

    def test_temp_swap_also_passes(self):
        write(L / "lessons" / LID / "swap.py", "a = 3\nb = 5\ntemp = a\na = b\nb = temp\nprint(a, b)\n")
        out = ev(["swap-1", "swap-2"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_hardcoded_swap_fails(self):
        write(L / "lessons" / LID / "swap.py", "a = 3\nb = 5\nprint(5, 3)\n")
        out = ev(["swap-1", "swap-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])

    def test_printing_the_raw_set_fails(self):
        src = (D / "reference" / "kinds.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "kinds.py", src.replace("sorted(nov_kinds & dec_kinds)", "nov_kinds & dec_kinds"))
        out = ev(["kinds-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("sorted", out.results[0].detail)

    def test_counting_without_set_fails(self):
        src = (D / "reference" / "kinds.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "kinds.py", src.replace("len(nov_kinds)", "len(nov)"))
        out = ev(["kinds-1"])
        self.assertFalse(out.results[0].ok)

    def test_hardcoded_kinds_fails_the_swap(self):
        write(L / "lessons" / LID / "kinds.py", 'nov = ["餐飲", "交通", "餐飲", "娛樂", "交通", "餐飲"]\n'
              'print("11 月一共 6 筆，花在 3 種分類")\nprint("兩個月都有", ["交通", "餐飲"])\nprint("只有 11 月有", ["娛樂"])\n')
        out = ev(["kinds-1", "kinds-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])


if __name__ == "__main__":
    unittest.main()
