"""1-10〈while 迴圈〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

重點是逾時（總企劃 1-10：check 有逾時設定）：
  - run 題的 timeout（1-10 加在 RunCheck，只對寫了它的題目生效）：學員的 while 停不下來，5 秒就停、說可能是無窮迴圈，stuck_hint 給白話。
  - 第③圈 inputs_text（1-6 的模式）加兩個只對寫了它的 checks.json 生效的旗標：stuck_note（壞版本卡在無窮迴圈、被逾時停下來，
    算抓到、note 寫卡住而不是當掉，總結多印兩行）、eof_hint（迴圈會一直問到 q，inputs.txt 沒有 q 時的白話）。
三個壞版本：q 也算成一筆（主角，最後一行打 q 就抓得到）、continue 跳過了「再問一次」（只有空白的一行會卡住）、合計沒有累加（要打兩筆以上）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import time
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l110"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-10"
D = COURSE / "lessons" / LID
T_IN = (D / "answers" / "inputs.txt").read_text(encoding="utf-8")
T_EXP = (D / "answers" / "expected.txt").read_text(encoding="utf-8")
# 影片裡熊的第一版：打兩筆再打 q（沒有空白的一行）→ 壞版本 2 溜過去；第二版在中間加一行空白 → 壞版本 2 卡住、被逾時停下來
BEAR_IN = "120\n85\nq\n"
BEAR_IN2 = "120\n\n85\nq\n"
BEAR_EXP = "一共 2 筆，合計 205 元\n"


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


def record(src: str) -> None:
    write(L / "lessons" / LID / "record.py", src)


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Chaff(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_inputs_catch_all_three_and_say_one_got_stuck(self):
        self.assertEqual(T_IN, "120\n\n85\nq\n")
        t0 = time.monotonic()
        out = r3(T_IN, T_EXP)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 2 行抓到")   # 一共 4 筆（老師的 expected.txt 第 1 行是 # 說明）
        self.assertEqual(part(out, "m2").note, "被第 2 行抓到（這個壞版本卡住了、跑不完，你的檢查抓到它）")
        self.assertEqual(part(out, "m3").note, "被第 2 行抓到")   # 合計 85 元
        self.assertIn("你的預期輸出把 3 個壞版本全部抓到了。", out.summaries)
        self.assertIn("  其中 1 個卡在迴圈裡停不下來：", out.summaries)
        self.assertIn("  check 等了 5 秒，把它停下來，算你抓到。", out.summaries)
        self.assertLess(time.monotonic() - t0, 25)   # 逾時 5 秒，不會等到環境的 30 秒

    def test_bear_first_inputs_let_the_blank_line_slip(self):
        out = r3(BEAR_IN, BEAR_EXP)
        self.assertTrue(part(out, "count").ok and part(out, "wheat").ok, [(r.id, r.detail) for r in out.results])
        self.assertTrue(part(out, "m1").ok and part(out, "m3").ok)
        self.assertFalse(part(out, "m2").ok)
        self.assertIn("空白的一行", part(out, "m2").detail)
        self.assertIn("你的預期輸出抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)
        self.assertFalse(any("卡在迴圈裡" in x for x in out.summaries))

    def test_bear_second_inputs_catch_all(self):
        out = r3(BEAR_IN2, BEAR_EXP)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_q_counted_version_is_caught_by_any_inputs_ending_with_q(self):
        for inp, exp in (("q\n", "一共 0 筆，合計 0 元\n"), ("120\nq\n", "一共 1 筆，合計 120 元\n")):
            out = r3(inp, exp)
            self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
            self.assertTrue(part(out, "m1").ok, inp)

    def test_one_amount_lets_the_total_bug_slip(self):
        out = r3("120\nq\n", "一共 1 筆，合計 120 元\n")
        self.assertEqual([part(out, m).ok for m in ("m1", "m2", "m3")], [True, False, False])
        self.assertIn("打兩筆以上", part(out, "m3").detail)

    def test_bear_counting_q_himself_fails_on_the_reference(self):
        out = r3(BEAR_IN, "一共 3 筆，合計 205 元\n")
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn("第 1 行「一共 3 筆，合計 205 元」跟正確版印出來的不一樣", r.detail)

    def test_missing_q_explains_the_loop_keeps_asking(self):
        out = r3("120\n85\n", BEAR_EXP)
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn("inputs.txt 的 2 行都讀完了，正確版還在問", r.detail)
        self.assertIn("最後一行要寫 q", r.detail)
        self.assertNotIn("程式要問 1 次", r.detail)

    def test_amount_with_yuan_or_capital_q_crashes_the_reference(self):
        for inp in ("120元\nq\n", "120\nQ\n"):
            out = r3(inp, BEAR_EXP)
            r = part(out, "wheat")
            self.assertFalse(r.ok, inp)
            self.assertIn("讓正確版也當掉了", r.detail)
            self.assertIn("大寫的 Q", r.detail)

    def test_prompts_copied_from_the_terminal_are_fine(self):
        out = r3(BEAR_IN, "金額，打 q 結束：金額，打 q 結束：金額，打 q 結束：一共 2 筆，合計 205 元\n")
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)

    def test_start_files_are_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你的預期輸出寫了 0 行，這課要至少 1 行（還有 1 行有「？」沒填完）", part(out, "count").detail)

    def test_crlf_and_bom_are_fine(self):
        out = r3(BEAR_IN2.replace("\n", "\r\n"), "﻿# 我的預期\r\n" + BEAR_EXP.replace("\n", "\r\n"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_one_six_inputs_text_has_no_new_flags(self):
        """1-6 的 inputs_text 照舊：沒有 stuck_note、eof_hint（行為一格不變）。"""
        les = grader.load_lesson("1-6", COURSE)
        spec = next(c for c in les.checks if c["id"] == "r3")
        self.assertEqual(spec["mode"], "inputs_text")
        self.assertNotIn("stuck_note", spec)
        self.assertNotIn("eof_hint", spec)


class RecordRuns(unittest.TestCase):
    def setUp(self):
        start()

    def test_reference_passes_and_start_does_not(self):
        out = ev(["rec-1", "rec-2", "rec-3"])
        self.assertFalse(any(r.ok for r in out.results))
        shutil.copy(D / "reference" / "record.py", L / "lessons" / LID / "record.py")
        out = ev(["rec-1", "rec-2", "rec-3"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_priming_read_version_also_passes(self):
        record('total = 0\ntext = input("金額，打 q 結束：")\nwhile text != "q":\n    if text != "":\n        total = total + int(text)\n'
               '    text = input("金額，打 q 結束：")\nprint("一共", total, "元")\n')
        out = ev(["rec-1", "rec-2", "rec-3"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_forgot_to_ask_again_is_stopped_in_five_seconds(self):
        """果凍兔的版本：迴圈裡少了「再問一次」，一直印 → 印太多被停下來；不印的話 → 5 秒逾時。"""
        record('total = 0\ntext = input("金額，打 q 結束：")\nwhile text != "q":\n    total = total + int(text)\n'
               '    print("目前合計", total, "元")\nprint("一共", total, "元")\n')
        t0 = time.monotonic()
        r = ev(["rec-1"]).results[0]
        self.assertFalse(r.ok)
        self.assertTrue("印了太多東西" in r.detail or "跑了 5 秒還沒結束" in r.detail, r.detail)
        self.assertIn("每一圈都要再問一次金額", r.detail)
        self.assertLess(time.monotonic() - t0, 25)
        record('total = 0\ntext = input("金額，打 q 結束：")\nwhile text != "q":\n    total = total + int(text)\nprint("一共", total, "元")\n')
        t0 = time.monotonic()
        r = ev(["rec-1"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("跑了 5 秒還沒結束，被停下來了：可能有無窮迴圈。", r.detail)
        self.assertIn("按 Ctrl+C", r.detail)
        self.assertLess(time.monotonic() - t0, 15)

    def test_same_file_stuck_once_is_not_waited_again(self):
        record('total = 0\ntext = input("金額，打 q 結束：")\nwhile text != "q":\n    total = total + int(text)\nprint("一共", total, "元")\n')
        t0 = time.monotonic()
        out = ev(["rec-1", "rec-2", "rec-3"])
        self.assertFalse(any(r.ok for r in out.results))
        self.assertIn("這題先不再等一次", out.results[2].detail)
        self.assertLess(time.monotonic() - t0, 15)

    def test_continue_skipping_the_reask_gets_the_continue_hint(self):
        record('total = 0\ntext = input("金額，打 q 結束：")\nwhile text != "q":\n    if text == "":\n        continue\n'
               '    total = total + int(text)\n    text = input("金額，打 q 結束：")\nprint("一共", total, "元")\n')
        out = ev(["rec-1", "rec-2", "rec-3"])
        self.assertEqual([r.ok for r in out.results], [True, True, False])
        self.assertIn("跑了 5 秒還沒結束", out.results[2].detail)
        self.assertIn("continue 會直接跳回 while", out.results[2].detail)

    def test_no_continue_crashes_on_the_blank_line(self):
        record('total = 0\nwhile True:\n    text = input("金額，打 q 結束：")\n    if text == "q":\n        break\n'
               '    total = total + int(text)\nprint("一共", total, "元")\n')
        out = ev(["rec-1", "rec-2", "rec-3"])
        self.assertEqual([r.ok for r in out.results], [True, True, False])
        self.assertIn("ValueError", out.results[2].detail)
        self.assertIn("continue", out.results[2].detail)

    def test_run_checks_without_timeout_keep_the_environment_default(self):
        les = grader.load_lesson("1-9", COURSE)
        self.assertTrue(all("timeout" not in c for c in les.checks if c["type"] == "run"))


class Max10(unittest.TestCase):
    def setUp(self):
        start()

    def test_reference_passes_and_start_does_not(self):
        out = ev(["max-1", "max-2", "max-3"])
        self.assertFalse(any(r.ok for r in out.results))
        shutil.copy(D / "reference" / "max10.py", L / "lessons" / LID / "max10.py")
        out = ev(["max-1", "max-2", "max-3"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_count_before_break_counts_q(self):
        src = (D / "reference" / "max10.py").read_text(encoding="utf-8")
        moved = src.replace("    count = count + 1\n", "").replace('    text = input("金額，打 q 結束：")\n',
                                                                    '    text = input("金額，打 q 結束：")\n    count = count + 1\n')
        write(L / "lessons" / LID / "max10.py", moved)
        out = ev(["max-1", "max-2", "max-3"])
        self.assertEqual([r.ok for r in out.results], [True, False, False])
        self.assertIn("break 的下面", out.results[1].detail)

    def test_tutor_style_print_with_commas_is_fine(self):
        src = (D / "reference" / "max10.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "max10.py", src.replace('print(f"一共 {count} 筆，合計 {total} 元")', 'print("一共", count, "筆，合計", total, "元")'))
        out = ev(["max-1", "max-2", "max-3"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results])

    def test_no_cap_crashes_at_the_end_of_input(self):
        src = (D / "reference" / "max10.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "max10.py", src.replace("while count < 10:", "while True:"))
        out = ev(["max-1", "max-2", "max-3"])
        self.assertEqual([r.ok for r in out.results], [False, True, True])
        self.assertIn("EOFError", out.results[0].detail)
        self.assertIn("count < 10", out.results[0].detail)


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_loops(self):
        answer("loops.txt", ["4", "4 次", "0", "c"])
        out = ev(["loops"])
        self.assertEqual([r.ok for r in out.results], [True] * 4, [r.detail for r in out.results])
        answer("loops.txt", ["5", "3", "1", "A"])
        out = ev(["loops"])
        self.assertEqual([r.ok for r in out.results], [False] * 4)

    def test_lead_quiz(self):
        answer("lead_quiz.txt", ["B", "3", "10"])
        out = ev(["lead"])
        self.assertEqual([r.ok for r in out.results], [True] * 3, [r.detail for r in out.results])
        answer("lead_quiz.txt", ["A", "2", "9"])
        out = ev(["lead"])
        self.assertEqual([r.ok for r in out.results], [False] * 3)


class FullRun(unittest.TestCase):
    def test_full_run_through_check_py(self):
        """check.py 1-10：全對 18 題，第③圈的總結看得到逾時那兩行。"""
        start()
        home = fresh_dir("l110_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_check(["start", "1-10"], env, stdin="")
        self.assertIn("uv run check.py 1-10", r.stdout)
        work = L / "lessons" / LID
        for f in ("record.py", "max10.py"):
            shutil.copy(D / "reference" / f, work / f)
        write(work / "inputs.txt", BEAR_IN2)
        write(work / "expected.txt", BEAR_EXP)
        answer("loops.txt", ["4", "4", "0", "C"])
        answer("lead_quiz.txt", ["B", "3", "10"])
        r = run_check(["1-10", "--predict", "18", "--no-review"], env)
        self.assertIn("18／18", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的預期輸出把 3 個壞版本全部抓到了。", r.stdout)
        self.assertIn("check 等了 5 秒，把它停下來，算你抓到。", r.stdout)
        for line in r.stdout.splitlines():   # VHS 錄影 70 欄：每行壓在 68 欄內
            self.assertLessEqual(sum(2 if ord(ch) > 0x2E7F else 1 for ch in line), 70, line)


if __name__ == "__main__":
    unittest.main()
