"""1-15〈dict：用名字找資料〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 加了三個只對寫了它的課生效的欄位（1-15 起）：
  - special.json 規則的 src：「需求有問題」照這一行的程式比對（正規式），而且這一行在正確版上真的不成立才算對（judge_src_mark）；
  - chaff 的 min_req_marks：至少要有幾行標「需求有問題」，還沒有就多一題沒過的（sreq，題數跟標了以後一樣）；
  - answers 題目的 keywords／reject：自己寫一句話，每一組關鍵字至少要有一個、reject 的一個都不能有（需求修正補的規則）。
第③圈的壞版本：m1 把占比寫回原本的 totals（只看交回的抓不到）、m2 round 到整數、m3 花 0 元的分類不見了。
需求卡第 4 條「加總要顯示 100%」：正確版 160、100、40 → 53.3＋33.3＋13.3＝99.9，是需求沒定規則（主角），標「# 需求有問題」。
light.py 的 swap 在 limits 裡多加一燈：把燈號寫死在 if／elif 的找不到 limits 那一行就過不了。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l115"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-15"
D = COURSE / "lessons" / LID
IMP = "from share import shares\n"
DATA = 't = {"餐飲": 160, "交通": 100, "娛樂": 40}\nr = shares(t)\n'
# 影片裡熊的第一版：三條檢查都抓到壞版本，需求卡第 4 條（加總 100）在正確版上不成立
BEAR_BODY = (IMP + "\n" + DATA +
             "# 每一類＝小計 ÷ 全部 × 100，留到小數一位\nassert r == {\"餐飲\": 53.3, \"交通\": 33.3, \"娛樂\": 13.3}\n"
             "# 不能動到原本的 totals\nassert t == {\"餐飲\": 160, \"交通\": 100, \"娛樂\": 40}\n"
             "# 花 0 元的分類也要有\nz = shares({\"餐飲\": 50, \"醫療\": 0})\nassert z == {\"餐飲\": 100.0, \"醫療\": 0.0}\n"
             "# 加總要顯示 100%\n")
BEAR_V1 = BEAR_BODY + "assert round(sum(r.values()), 1) == 100\n"
BEAR_V2 = BEAR_BODY + "assert round(sum(r.values()), 1) == 100  # 需求有問題\n"
SUM_LINE = BEAR_V1.count("\n")   # 加總那一行是第幾行


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
    write(L / "lessons" / LID / "checks_share.py", text)
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

    def test_teacher_checks_catch_all_three_and_mark_is_right(self):
        out = r3((D / "answers" / "checks_share.py").read_text(encoding="utf-8"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 9 行抓到")    # 原本的 totals 被改掉了
        self.assertEqual(part(out, "m2").note, "被第 7 行抓到")    # 53 不是 53.3
        self.assertEqual(part(out, "m3").note, "被第 11 行抓到")   # 醫療不見了
        self.assertIn("你的檢查把 3 個壞版本全部抓到了。", out.summaries)

    def test_bear_v1_sum_line_fails_on_the_reference(self):
        out = r3(BEAR_V1)
        self.assertTrue(part(out, "count").ok)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, True, True])
        w = part(out, "wheat")
        self.assertFalse(w.ok)
        self.assertIn(f"第 {SUM_LINE} 行", w.detail)
        self.assertIn("99.9", w.detail)
        self.assertIn("「# 需求有問題」", w.detail)
        self.assertFalse(part(out, "sreq").ok)          # 還沒標：多一題沒過的
        self.assertIn("3 個壞版本全部抓到了", " ".join(out.summaries))

    def test_bear_v2_mark_is_judged_right(self):
        out = r3(BEAR_V2)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        s = part(out, f"s{SUM_LINE}")
        self.assertIn("少了 0.1", s.note)
        self.assertFalse(any(r.id.endswith("sreq") for r in out.results))

    def test_item_count_same_before_and_after_marking(self):
        """標之前 sreq 佔一題、標了以後 s<行號> 佔一題：猜題數的時候總數一樣。"""
        self.assertEqual(len(r3(BEAR_V1).results), len(r3(BEAR_V2).results))

    def test_plain_sum_without_round_is_also_accepted(self):
        out = r3(BEAR_BODY + "assert sum(r.values()) == 100  # 需求有問題\n")
        self.assertTrue(part(out, f"s{SUM_LINE}").ok, part(out, f"s{SUM_LINE}").detail)

    def test_mark_on_a_sum_that_holds_is_wrong(self):
        """300、100 剛好整除，加總就是 100：這一行在正確版上成立，標了需求有問題不算對。"""
        out = r3(BEAR_BODY + "assert round(sum(shares({\"餐飲\": 300, \"交通\": 100}).values()), 1) == 100  # 需求有問題\n")
        s = part(out, f"s{SUM_LINE}")
        self.assertFalse(s.ok)
        self.assertIn("在正確版上成立", s.detail)
        self.assertIn("160、100、40", s.detail)

    def test_mark_on_a_wrong_value_line_is_wrong(self):
        """自己算錯的值（53.4）標成需求有問題：需求卡寫得很清楚，不是需求的問題。"""
        out = r3(BEAR_BODY + "assert r[\"餐飲\"] == 53.4  # 需求有問題\n")
        s = part(out, f"s{SUM_LINE}")
        self.assertFalse(s.ok)
        self.assertIn("需求卡寫得很清楚", s.detail)

    def test_all_zero_is_a_known_crash(self):
        """全部都是 0 元：正確版除以 0 會當掉，標「已知會當掉」照舊判成對的。"""
        out = r3(BEAR_V2 + "assert shares({\"餐飲\": 0}) == {\"餐飲\": 0.0}  # 已知會當掉\n")
        s = part(out, f"s{SUM_LINE + 1}")
        self.assertTrue(s.ok, s.detail)
        self.assertIn("ZeroDivisionError", s.note)

    def test_without_the_sum_line_sreq_explains(self):
        out = r3(BEAR_BODY)
        self.assertTrue(part(out, "wheat").ok)
        r = part(out, "sreq")
        self.assertFalse(r.ok)
        self.assertIn("加總要顯示 100%", r.detail)

    def test_only_returned_value_lets_m1_slip(self):
        """只看交回的（不再比原本的 totals）：壞版本 1 溜過去，提示問原本的 totals。"""
        body = (IMP + DATA + "assert r == {\"餐飲\": 53.3, \"交通\": 33.3, \"娛樂\": 13.3}\n"
                "assert shares({\"餐飲\": 50, \"醫療\": 0}) == {\"餐飲\": 100.0, \"醫療\": 0.0}\n"
                "assert len(r) == 3\n")
        out = r3(body)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [False, True, True])
        self.assertIn("原本的 totals", part(out, "m1").detail)

    def test_whole_number_shares_do_not_catch_m2(self):
        """75.0 和 25.0 這種整數占比，round 到整數也一樣（75 == 75.0）：要用有小數的例子。"""
        body = (IMP + "assert shares({\"餐飲\": 300, \"交通\": 100}) == {\"餐飲\": 75.0, \"交通\": 25.0}\n"
                "t = {\"餐飲\": 300, \"交通\": 100}\nr = shares(t)\nassert t == {\"餐飲\": 300, \"交通\": 100}\n"
                "assert shares({\"餐飲\": 50, \"醫療\": 0}) == {\"餐飲\": 100.0, \"醫療\": 0.0}\n")
        out = r3(body)
        self.assertFalse(part(out, "m2").ok)
        self.assertIn("小數一位", part(out, "m2").detail)

    def test_dict_order_does_not_matter_for_equality(self):
        out = r3(IMP + DATA + "assert r == {\"娛樂\": 13.3, \"交通\": 33.3, \"餐飲\": 53.3}\n"
                 "assert t == {\"餐飲\": 160, \"交通\": 100, \"娛樂\": 40}\nassert len(r) == 3\n")
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)

    def test_start_file_needs_three(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("3", part(out, "count").detail)


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_predict_dict_quiz_and_fix(self):
        answer("predict.txt", ["75", "C", "A", "B", "公車"])
        answer("dict_quiz.txt", ["B", "A", "C"])
        answer("req_fix.txt", ["B", "誤差歸到最大的一類", "53.4"])
        out = ev(["predict", "dictq", "fix"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_predict_common_mistakes(self):
        answer("predict.txt", ["1", "A", "C", "A", "午餐"])
        out = ev(["predict"])
        self.assertEqual([r.ok for r in out.results], [False] * 5)
        self.assertIn("名字", out.results[0].detail)

    def test_rule_in_other_words(self):
        for rule in ("少掉的 0.1 加給金額最高的那一類", "四捨五入的差額，算到最多的分類", "把誤差補到最大類",
                     # 1-15 第一輪驗收：原本被擋的合理寫法
                     "最大的那一類用 100 減掉其他類", "少掉的 0.1 加到餐飲", "誤差給最大的一類，其他（包括最小的）不變",
                     # Codex 第二輪：否定的是最小、補給最大的寫法要算對
                     "誤差不給最小的，補到最大的一類"):
            answer("req_fix.txt", ["B", rule, "53.4%"])
            out = ev(["fix"])
            self.assertTrue(all(r.ok for r in out.results), (rule, [(r.id, r.detail) for r in out.results]))
            start()

    def test_rule_with_smallest_or_without_whom_fails(self):
        for rule in ("誤差歸到最小的一類", "加總不用是 100", "最大",
                     # 1-15 第一輪驗收：原本被放過的錯寫法（說反、平均分、沒定規則）
                     "最大的一類不要動，誤差平均分", "誤差不能歸到最大的一類", "加總最多差 0.1 也算 100%",
                     # Codex 第二輪：否定句（reject_re）
                     "誤差不要歸給最大的一類", "少掉的給最小的"):
            answer("req_fix.txt", ["B", rule, "53.4"])
            out = ev(["fix"])
            self.assertFalse(out.results[1].ok, rule)
            self.assertIn("誤差歸到最大的一類", out.results[1].detail)
            start()

    def test_fix_wrong_choice_and_number(self):
        answer("req_fix.txt", ["A", "誤差歸到最大的一類", "53.3"])
        out = ev(["fix"])
        self.assertEqual([r.ok for r in out.results], [False, True, False])

    def test_fix_two_letters_is_not_a_choice(self):
        answer("req_fix.txt", ["A 或 B", "誤差歸到最大的一類", "53.4"])
        out = ev(["fix"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("只能選一個", out.results[0].detail)

    def test_empty_rule_asks_to_answer(self):
        out = ev(["fix"])
        self.assertIn("還沒作答", out.results[1].detail)


class Programs(unittest.TestCase):
    def setUp(self):
        start()

    def test_references_pass_and_starts_do_not(self):
        ids = ["totals-1", "totals-2", "light-1", "light-2", "percent-1", "percent-2"]
        out = ev(ids)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        for f in ("totals.py", "light.py", "percent.py"):
            shutil.copy(D / "reference" / f, L / "lessons" / LID / f)
        out = ev(ids)
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_square_brackets_on_empty_dict_crash_with_keyerror(self):
        src = (D / "reference" / "totals.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "totals.py", src.replace("totals.get(kind, 0)", "totals[kind]"))
        out = ev(["totals-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("KeyError", out.results[0].detail)

    def test_print_with_commas_also_passes(self):
        write(L / "lessons" / LID / "totals.py",
              'entries = [("餐飲", 120), ("交通", 30), ("餐飲", 85), ("交通", 45), ("娛樂", 200)]\n'
              "totals = {}\ncounts = {}\nfor kind, amount in entries:\n"
              "    totals[kind] = totals.get(kind, 0) + amount\n    counts[kind] = counts.get(kind, 0) + 1\n"
              'for kind in totals:\n    print(kind, totals[kind], "元，", counts[kind], "筆")\n')
        out = ev(["totals-1", "totals-2"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_hardcoded_totals_fails_the_swap(self):
        write(L / "lessons" / LID / "totals.py",
              'entries = [("餐飲", 120), ("交通", 30), ("餐飲", 85), ("交通", 45), ("娛樂", 200)]\n'
              'print("餐飲 205 元，2 筆")\nprint("交通 75 元，2 筆")\nprint("娛樂 200 元，1 筆")\n')
        out = ev(["totals-1", "totals-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])

    def test_if_elif_lights_fail_the_extra_light(self):
        """1-9 的 if／elif 寫法四組都對，可是 limits 多一燈時找不到那一行：多一燈要改程式。"""
        write(L / "lessons" / LID / "light.py",
              'spent = int(input("這個月花了多少？"))\nif spent <= 799:\n    print("綠燈")\nelif spent <= 1000:\n'
              '    print("黃燈")\nelse:\n    print("紅燈")\n')
        out = ev(["light-1", "light-2"])
        self.assertEqual([r.ok for r in out.results], [True, False])
        self.assertIn("limits", out.results[1].detail)

    def test_limits_kept_but_ifs_hardcoded_fail_the_extra_light(self):
        write(L / "lessons" / LID / "light.py",
              'spent = int(input("這個月花了多少？"))\nlimits = {"綠燈": 799, "黃燈": 1000}\n'
              'if spent <= limits["綠燈"]:\n    print("綠燈")\nelif spent <= limits["黃燈"]:\n    print("黃燈")\nelse:\n    print("紅燈")\n')
        out = ev(["light-2"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("1100", out.results[0].detail)

    def test_less_than_instead_of_at_most_misses_exactly_1000(self):
        src = (D / "reference" / "light.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "light.py", src.replace("spent <= top", "spent < top"))
        out = ev(["light-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("1000", out.results[0].detail)

    def test_sum_of_dict_adds_keys(self):
        src = (D / "reference" / "percent.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "percent.py", src.replace("sum(totals.values())", "sum(totals)"))
        out = ev(["percent-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("TypeError", out.results[0].detail)

    def test_fstring_percent_also_passes(self):
        write(L / "lessons" / LID / "percent.py",
              'totals = {"餐飲": 205, "交通": 75, "娛樂": 200}\nwhole = sum(totals.values())\n'
              'for kind, amount in totals.items():\n    print(f"{kind} {amount / whole * 100:.1f}%")\n')
        out = ev(["percent-1", "percent-2"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])


if __name__ == "__main__":
    unittest.main()
