"""1-22〈錯誤處理：try／except／else／finally 與 raise〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

grader 加的東西（只對寫了它的題目生效）：call 的 raises／msg_has（這一次呼叫應該丟出 ValueError、錯誤訊息裡要有 -35）；
chaff assert 模式的 try_checks（最外層的 try（裡面有 assert）整個算一條檢查：學員用 try／except ValueError as e／else: assert False
寫「應該丟出錯誤」）；ast_require 的 named_except（要有 except ValueError、不能有光禿禿的 except:）。
第③圈：學員的檢查拿去跑課程的正確版和 3 個 AI 寫錯的版本（m1 看不懂的用光禿禿的 except 吞掉交回 0、m2 負數丟 TypeError、m3 訊息裡沒有那個值）；
影片裡熊的三條：第一條（一般的金額）一個都抓不到，第二條（一百要丟 ValueError）抓到 m1，第三條（-35 要丟 ValueError、訊息裡有 -35）抓到 m2、m3
（思考站「丟錯類型的版本，哪一條抓得到？」答案是第三條）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l122"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-22"
D = COURSE / "lessons" / LID
IMP = "from money import to_yuan\n"
C1 = 'assert to_yuan("1,200元") == 1200\n'
C2 = 'try:\n    to_yuan("一百")\nexcept ValueError as e:\n    assert "一百" in str(e)\nelse:\n    assert False\n'
C3 = 'try:\n    to_yuan("-35")\nexcept ValueError as e:\n    assert "-35" in str(e)\nelse:\n    assert False\n'
BEAR = IMP + "# 一般的金額\n" + C1 + "# 看不懂的要丟 ValueError\n" + C2 + "# 負數要丟 ValueError，訊息裡有那個值\n" + C3   # 影片裡熊寫的三條


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
    write(mine("checks_money.py"), text)
    return ev(["r3"])


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def quiz_blocks(name: str) -> list[str]:
    """作答檔每一題的程式（「#   」開頭、不是選項的那幾行；第 3 題沒有程式的回空字串）。"""
    blocks = (D / "start" / name).read_text(encoding="utf-8").split("\n答：")[:-1]
    out = []
    for blk in blocks:
        body = blk.split("題：")[-1].splitlines()
        code = [ln[4:] for ln in body if ln.startswith("#   ") and not ln.startswith(("#   A.", "#   B.", "#   C."))]
        code = [c for c in code]
        out.append("\n".join(code) + "\n" if code else "")
    return out


def run_quiz(code: str) -> tuple[list[str], str]:
    """跑一題的程式：印出來的每一行、沒接住的錯誤種類（沒有＝空字串）。"""
    buf = io.StringIO()
    err = ""
    with contextlib.redirect_stdout(buf):
        try:
            exec(compile(code, "<q>", "exec"), {})
        except Exception as exc:  # noqa: BLE001
            err = type(exc).__name__
    return buf.getvalue().splitlines(), err


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
        """以為出錯那一行後面還會跑、以為 finally 只在沒出錯時走、以為 except ValueError 也接得到 TypeError。"""
        answer("predict.txt", ["A", "B", "A"])
        out = ev(["predict"])
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])

    def test_answers_match_python(self):
        key = json.loads((D / "answers" / "predict.json").read_text(encoding="utf-8"))
        codes = quiz_blocks("predict.txt")
        got = [run_quiz(c) for c in codes]
        self.assertEqual(got[0], (["A", "C", "D"], ""))
        self.assertEqual(got[1], (["記下 85", "下一筆", "看不懂", "下一筆"], ""))
        self.assertEqual(got[2], ([], "TypeError"))
        self.assertEqual([q["accept"] for q in key["questions"]], [["B"], ["A"], ["C"]])
        self.assertEqual(key["questions"][0]["choices"]["B"], "A C D")
        self.assertEqual(key["questions"][1]["choices"]["A"], "記下 85、下一筆、看不懂、下一筆")


class Bare(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("bare.txt", ["B", "C", "A"])
        out = ev(["bare"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_answers_match_python(self):
        """第 1 題光禿禿的 except 把打錯字（NameError）吞掉，只印「請再輸入一次」；第 2 題 except ValueError 接不到 NameError。"""
        codes = quiz_blocks("bare.txt")
        self.assertEqual(run_quiz(codes[0]), (["請再輸入一次"], ""))
        self.assertEqual(run_quiz(codes[1]), ([], "NameError"))
        self.assertEqual(codes[2], "")

    def test_bare_except_swallows_keyboard_interrupt(self):
        """回顧題 r3、影片第②圈：光禿禿的 except 連 KeyboardInterrupt（Control C）也接住；except Exception 接不到它。"""
        def bare():
            try:
                raise KeyboardInterrupt
            except:  # noqa: E722
                return "接住了"
        self.assertEqual(bare(), "接住了")
        self.assertFalse(issubclass(KeyboardInterrupt, Exception))


class Money(unittest.TestCase):
    IDS = ["yuan-1", "raise-neg", "raise-word"]

    def setUp(self):
        start()

    def test_start_has_no_raise_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertEqual([r.ok for r in out.results], [True, False, True])
        self.assertIn("沒有丟出錯誤，交回了 -35", out.results[1].detail)
        write(mine("money.py"), ref("money.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def _with(self, old: str, new: str) -> str:
        src = ref("money.py")
        assert old in src, old
        return src.replace(old, new)

    def test_wrong_type(self):
        write(mine("money.py"), self._with("raise ValueError(", "raise TypeError("))
        out = ev(["raise-neg"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("丟出的是 TypeError", out.results[0].detail)

    def test_message_without_value(self):
        write(mine("money.py"), self._with('raise ValueError(f"金額不能是負數：{text}")', 'raise ValueError("金額不能是負數")'))
        out = ev(["raise-neg"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("裡沒有 -35", out.results[0].detail)

    def test_subclass_counts(self):
        """丟出 ValueError 的子類別也算（UnicodeError 是 ValueError 的一種）。"""
        write(mine("money.py"), self._with('raise ValueError(f"金額不能是負數：{text}")', 'raise UnicodeError(f"金額不能是負數：{text}")'))
        out = ev(["raise-neg"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_swallowed_in_to_yuan(self):
        """在 to_yuan 裡把 int 的錯接住、交回 0（AI 寫錯的版本 1 那樣）：一百不丟錯，raise-word 抓到。"""
        src = self._with("    amount = int(text)\n", "    try:\n        amount = int(text)\n    except ValueError:\n        return 0\n")
        write(mine("money.py"), src)
        out = ev(["raise-word"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("交回了 0", out.results[0].detail)

    def test_broke_normal_amount(self):
        write(mine("money.py"), self._with("    return amount\n", "    return text\n"))
        out = ev(["yuan-1"])
        self.assertFalse(out.results[0].ok)


class Add(unittest.TestCase):
    IDS = ["add-1", "add-2"]

    def setUp(self):
        start()
        write(mine("money.py"), ref("money.py"))

    def test_start_crashes_and_reference_passes(self):
        out = ev(self.IDS)
        self.assertEqual([r.ok for r in out.results], [False, True])   # 起點檔第一次就打對（85元）也記得下來，只有亂輸入會當掉
        self.assertIn("ValueError", out.results[0].detail)
        write(mine("add.py"), ref("add.py"))
        out = ev(self.IDS)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_bare_except_refused(self):
        src = ref("add.py").replace("    except ValueError as e:\n        print(\"請再輸入一次。\", e)\n", "    except:\n        print(\"請再輸入一次。\", \"金額不能是負數：-35\")\n")
        write(mine("add.py"), src)
        out = ev(["add-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("不要用光禿禿的 except:", out.results[0].detail)

    def test_exception_is_ok_if_named(self):
        """except (ValueError, TypeError) 也寫明了 ValueError，算過。"""
        write(mine("add.py"), ref("add.py").replace("except ValueError as e:", "except (ValueError, TypeError) as e:"))
        out = ev(["add-1"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_forgot_break(self):
        write(mine("add.py"), ref("add.py").replace("        break\n", ""))
        out = ev(["add-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("break", out.results[0].detail)

    def test_money_without_raise_records_negative(self):
        """money.py 還沒加 raise：-35 被記下來（沒有「金額不能是負數」）。"""
        start()
        write(mine("add.py"), ref("add.py"))
        out = ev(["add-1"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("沒有看到應該要印的字", out.results[0].detail)

    def test_other_message_wording_ok(self):
        """錯誤訊息的寫法不限（AI 交回的版本寫「金額不可為負數」）：請再輸入一次的那一行有 -35 就算。"""
        write(mine("money.py"), ref("money.py").replace("金額不能是負數", "金額不可為負數"))
        write(mine("add.py"), ref("add.py"))
        out = ev(["add-1"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_try_without_except_message(self):
        """README 常見錯誤那一列的原文：try 後面沒有 except。"""
        p = subprocess.run([sys.executable, "-c", "try:\n    x = 1\nprint(x)\n"], capture_output=True, text=True)
        self.assertIn("SyntaxError: expected 'except' or 'finally' block", p.stderr)


class Tutor(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_then_filled(self):
        out = ev(["tutor"])
        self.assertFalse(out.results[0].ok)
        p = mine("tutor.md")
        txt = p.read_text(encoding="utf-8")
        for lab in ("AI 的建議：", "家教問我的：", "我的回答：", "我決定："):
            txt = txt.replace(lab + "\n", lab + "寫了一些字\n", 1)
        p.write_text(txt, encoding="utf-8")
        out = ev(["tutor"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)


class R3(unittest.TestCase):
    def setUp(self):
        start()
        write(mine("money.py"), ref("money.py"))

    def test_bear_three_checks_catch_all(self):
        out = r3(BEAR)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 5 行抓到")
        self.assertIn("被第", part(out, "m2").note)

    def test_each_check_alone(self):
        """熊的三條各自抓到哪幾個（影片的思考站：丟錯類型的 m2 只有第三條抓得到）。"""
        def caught(text):
            out = r3(IMP + text + C1.replace("1,200元", "120").replace("1200", "120") + C1)
            return [part(out, f"m{k}").ok for k in (1, 2, 3)]
        self.assertEqual(caught(C2), [True, False, False])
        self.assertEqual(caught(C3), [False, True, True])

    def test_start_examples_count_and_miss_m1(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)   # 起點檔只有 2 條
        self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
        self.assertEqual([part(out, f"m{k}").ok for k in (1, 2, 3)], [False, True, True])

    def test_bare_except_lets_wrong_type_slip(self):
        """負數那條寫成光禿禿的 except：丟 TypeError 的 m2 也被接住、溜過去；還有一行提醒。"""
        c3 = C3.replace("except ValueError as e:\n    assert \"-35\" in str(e)\n", "except:\n    pass\n")
        out = r3(BEAR.replace(C3, c3))
        self.assertTrue(part(out, "wheat").ok)
        self.assertFalse(part(out, "m2").ok)
        les = grader.load_lesson(LID, COURSE)
        ctx_notes = grader.evaluate(les, L, only=[c for c in les.checks if c["id"] == "r3"])
        self.assertTrue(any("光禿禿的 except:" in s for s in ctx_notes.summaries), ctx_notes.summaries)

    def test_valid_amount_in_try_fails_on_reference(self):
        """try 裡交的是合法的金額（120）：正確版不丟錯，走到 else 的 assert False，在正確版上就不成立。"""
        out = r3(BEAR.replace('to_yuan("-35")', 'to_yuan("35")'))
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("走到 else 的 assert False", part(out, "wheat").detail)

    def test_wrong_except_type_crashes_on_reference(self):
        out = r3(BEAR.replace("except ValueError as e:\n    assert \"-35\"", "except TypeError as e:\n    assert \"-35\""))
        self.assertFalse(part(out, "wheat").ok)
        self.assertIn("正確版丟出的是 ValueError", part(out, "wheat").detail)

    def test_try_without_assert_not_counted(self):
        out = r3(IMP + C1 + 'try:\n    to_yuan("一百")\nexcept ValueError:\n    print("接住了")\n' + C3)
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你寫了 2 條檢查", part(out, "count").detail)

    def test_plain_assert_mode_unchanged(self):
        """沒寫 try_checks 的課（1-20）照舊：try 裡的 assert 不算，還是提醒寫在最外層。"""
        les = grader.load_lesson("1-20", COURSE)
        spec = next(c for c in les.checks if c["id"] == "r3")
        self.assertNotIn("try_checks", spec)


class Green(unittest.TestCase):
    def setUp(self):
        start()

    def test_green_needs_raise_in_money(self):
        write(mine("checks_money.py"), BEAR)
        out = ev(["green"])
        self.assertFalse(out.results[0].ok)   # 起點檔的 money.py 還沒加 raise：-35 那條不成立
        write(mine("money.py"), ref("money.py"))
        out = ev(["green"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)


if __name__ == "__main__":
    unittest.main()
