"""1-6〈input、型別轉換，第一次認識函式呼叫〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

重點是第③圈 chaff 的新模式 inputs_text（只對寫了它的 checks.json 生效，1-1 的 expected_text 不受影響）：
  學員寫 inputs.txt（要打的字，一行一個）和 expected.txt（預期輸出），check 用 subprocess 把 inputs.txt 餵給正確版和 3 個壞版本
  （不靠 shell 的 <），拿掉每一行開頭的提示字（品項：、金額：）以後，一行一行、連總行數一起比。
三個壞版本：品項沒有 strip()（前後有空白才抓得到）、金額沒拿掉逗號（打 1,200 才當掉）、金額沒有 int()（印得出來，算還剩多少時當掉）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l16"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-6"
D = COURSE / "lessons" / LID
T_IN = (D / "answers" / "inputs.txt").read_text(encoding="utf-8")
T_EXP = (D / "answers" / "expected.txt").read_text(encoding="utf-8")
# 影片裡熊的 inputs.txt：品項沒有空白、金額有千分位逗號（他記得第②圈的 1,200）
BEAR_IN = "午餐\n1,200\n"
BEAR_EXP = "這週的餐費預算 3000 元\n記下來了：午餐 1200元\n這週還剩 1800 元\n"


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


def r3(inputs: str, expected: str) -> grader.Outcome:
    write(L / "lessons" / LID / "inputs.txt", inputs)
    write(L / "lessons" / LID / "expected.txt", expected)
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


class InputsText(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_inputs_catch_all_three(self):
        self.assertTrue(T_IN.startswith(" 聚餐 "), repr(T_IN))
        out = r3(T_IN, T_EXP)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 3 行抓到")   # 品項沒 strip：「記下來了： 聚餐  1200元」
        self.assertEqual(part(out, "m2").note, "被第 3 行抓到（這個版本跑到一半當掉了）")   # 1,200 當掉，只印了預算那一行
        self.assertEqual(part(out, "m3").note, "被第 4 行抓到（這個版本跑到一半當掉了）")   # 3000 - "1200" 當掉
        self.assertIn("你的預期輸出把 3 個壞版本全部抓到了。", out.summaries)

    def test_start_files_are_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你的預期輸出寫了 0 行，這課要至少 3 行（還有 1 行有「？」沒填完）", part(out, "count").detail)

    def test_bear_inputs_without_spaces_let_m1_slip(self):
        out = r3(BEAR_IN, BEAR_EXP)
        self.assertTrue(part(out, "count").ok and part(out, "wheat").ok, [(r.id, r.detail) for r in out.results])
        self.assertTrue(part(out, "m2").ok and part(out, "m3").ok)
        self.assertFalse(part(out, "m1").ok)
        self.assertIn("品項前後多打了空白", part(out, "m1").detail)
        self.assertIn("你的預期輸出抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)

    def test_plain_inputs_only_catch_the_missing_int(self):
        out = r3("午餐\n120\n", "這週的餐費預算 3000 元\n記下來了：午餐 120元\n這週還剩 2880 元\n")
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [False, False, True])

    def test_leading_space_alone_catches_m1(self):
        """前面一個空白就夠（行尾的空白看不到，也可能被編輯器拿掉）。"""
        out = r3(" 午餐\n1,200\n", BEAR_EXP)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_prompts_copied_from_the_terminal_are_fine(self):
        exp = "這週的餐費預算 3000 元\n品項：金額：記下來了：午餐 1200元\n這週還剩 1800 元\n"
        out = r3(BEAR_IN, exp)
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)

    def test_too_few_input_lines_explains_eof(self):
        out = r3("午餐\n", BEAR_EXP)
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn("inputs.txt 只有 1 行，程式要問 2 次（品項： 或 金額：）", r.detail)
        self.assertIn("EOFError", r.detail)

    def test_amount_with_yuan_makes_the_reference_crash(self):
        out = r3("午餐\n120元\n", BEAR_EXP)
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn("讓正確版也當掉了", r.detail)
        self.assertIn("ValueError", r.detail)
        self.assertIn("順序寫反了", r.detail)

    def test_comment_or_question_mark_in_inputs_is_refused(self):
        for text, want in (("# 我的輸入\n午餐\n120\n", "第 1 行是 # 開頭的說明"), ("午餐\n？\n", "第 2 行還是「？」"), ("\n\n", "是空的")):
            out = r3(text, BEAR_EXP)
            self.assertFalse(any(r.ok for r in out.results), text)
            self.assertIn(want, part(out, "count").detail, text)

    def test_wrong_expected_line_points_at_it(self):
        out = r3(BEAR_IN, BEAR_EXP.replace("1800", "1,800"))
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn("第 3 行「這週還剩 1,800 元」跟正確版印出來的不一樣", r.detail)

    def test_missing_budget_line_is_caught_by_the_line_count(self):
        out = r3(BEAR_IN, "記下來了：午餐 1200元\n這週還剩 1800 元\n")
        self.assertFalse(part(out, "count").ok)   # 只寫了 2 行
        out = r3(BEAR_IN, "記下來了：午餐 1200元\n這週還剩 1800 元\n這週的餐費預算 3000 元\n")
        self.assertFalse(part(out, "wheat").ok)

    def test_crlf_and_bom_are_fine(self):
        out = r3(" 午餐 \r\n1,200\r\n", "﻿# 我的預期\r\n" + BEAR_EXP.replace("\n", "\r\n"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_one_one_expected_text_is_untouched(self):
        """1-1 的 expected_text 照舊：沒有 inputs_file，也不拿掉提示字。"""
        les = grader.load_lesson("1-1", COURSE)
        spec = next(c for c in les.checks if c["id"] == "r3")
        self.assertEqual(spec["mode"], "expected_text")
        self.assertNotIn("inputs_file", spec)


class OtherChecks(unittest.TestCase):
    def setUp(self):
        start()

    def test_bill_reference_passes_and_start_does_not(self):
        out = ev(["bill1", "bill2", "bill3"])
        self.assertFalse(any(r.ok for r in out.results))
        shutil.copy(D / "reference" / "bill.py", L / "lessons" / LID / "bill.py")
        out = ev(["bill1", "bill2", "bill3"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_bill_without_replace_crashes_on_the_comma(self):
        src = (D / "reference" / "bill.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "bill.py", src.replace('.replace(",", "")', ""))
        out = ev(["bill1", "bill2", "bill3"])
        self.assertEqual([r.ok for r in out.results], [True, True, False])
        self.assertIn("ValueError", out.results[2].detail)
        self.assertIn("replace", out.results[2].detail)

    def test_bill_without_int_is_a_type_error(self):
        src = (D / "reference" / "bill.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "bill.py", src.replace('int(input("幾個人："))', 'input("幾個人：")'))
        r = ev(["bill1"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("TypeError", r.detail)

    def test_hard_coded_answer_fails_the_second_run(self):
        write(L / "lessons" / LID / "bill.py", 'total = input("總金額：")\npeople = input("幾個人：")\nprint("每人 362 元，零頭 2 元")\n')
        out = ev(["bill1", "bill2"])
        self.assertEqual([r.ok for r in out.results], [True, False])

    def test_guess_answers(self):
        answer("guess.txt", ["2", "10", "121", "100", "85.0", "123", "b", "C"])
        out = ev(["guess"])
        self.assertEqual([r.ok for r in out.results], [True] * 8, [r.detail for r in out.results])
        answer("guess.txt", ["4", "8", "1201", "錯誤", "85", "15", "A", "A"])
        out = ev(["guess"])
        self.assertEqual([r.ok for r in out.results], [False] * 8)

    def test_ai_ask_answers(self):
        answer("ai_ask.txt", ["B", "a", "，"])
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [True] * 3, [r.detail for r in out.results])
        answer("ai_ask.txt", ["A", "C", "0"])
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [False] * 3)

    def test_full_run_through_check_py(self):
        """check.py 1-06（課號補 0 也認得）：全對 19 題。"""
        home = fresh_dir("l16_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_check(["start", "1-06"], env, stdin="")
        self.assertIn("uv run check.py 1-6", r.stdout)
        work = L / "lessons" / LID
        shutil.copy(D / "reference" / "bill.py", work / "bill.py")
        write(work / "inputs.txt", T_IN)
        write(work / "expected.txt", T_EXP)
        answer("guess.txt", ["2", "10", "121", "100", "85.0", "123", "B", "C"])
        answer("ai_ask.txt", ["B", "A", "逗號"])
        r = run_check(["1-06", "--predict", "18", "--no-review"], env)
        self.assertIn("19／19", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的預期輸出把 3 個壞版本全部抓到了。", r.stdout)


if __name__ == "__main__":
    unittest.main()
