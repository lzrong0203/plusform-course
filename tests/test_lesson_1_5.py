"""1-5〈字串：索引、切片、方法、f-string〉：作業與 check 的回歸測試（第 1 級起每課自己一個測試檔，不改 test_regressions.py）。

重點是第③圈 cases 模式的新旗標 expect_tuple（只對寫了它的 checks.json 生效，1-3、1-4 不受影響）：
  右邊寫「"午餐", 120」：品項是文字（加引號）、金額是整數（不加引號、不寫「元」），check 把 split_item() 交回的 ("午餐", 120) 當 list 比，每個值的型別也比。
三個壞版本：split(" ") 只認半形空白（全形空白拆不開、int() 當掉）、split(" ") 以後拿第二段當金額（好幾個空白時是空的）、用 [:-1] 把「元」切掉（沒寫「元」時 85 變成 8）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l15"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "1-5"
D = COURSE / "lessons" / LID
TEACHER = (D / "answers" / "cases.txt").read_text(encoding="utf-8")
# 影片裡熊的六組：一般、沒寫元、好幾個空白、前後有空白，再加兩組一般的；沒有全形空白
BEAR6 = ('"午餐 120元" -> "午餐", 120\n"咖啡 85" -> "咖啡", 85\n"午餐   120元" -> "午餐", 120\n'
         '" 早餐 65元 " -> "早餐", 65\n"飲料 50元" -> "飲料", 50\n"晚餐 180元" -> "晚餐", 180\n')
FW = "　"


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


def cases(text: str) -> grader.Outcome:
    write(L / "lessons" / LID / "cases.txt", text)
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


class Cases(unittest.TestCase):
    def setUp(self):
        start()

    def test_teacher_answer_has_a_real_fullwidth_space_and_catches_all_three(self):
        self.assertIn(FW, TEACHER)
        out = cases(TEACHER)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(part(out, "m1").note, "被第 5 行抓到")   # 全形空白：split(" ") 拆不開
        self.assertEqual(part(out, "m2").note, "被第 4 行抓到")   # 好幾個空白：第二段是空的
        self.assertEqual(part(out, "m3").note, "被第 3 行抓到")   # 沒寫元：85 → 8
        self.assertIn("你的案例把 3 個壞版本全部抓到了。", out.summaries)

    def test_start_file_is_not_done(self):
        out = ev(["r3"])
        self.assertFalse(part(out, "count").ok)
        self.assertIn("你寫了 1 組案例，這課要至少 6 組", part(out, "count").detail)
        self.assertTrue(part(out, "wheat").ok)   # 範例那一行在正確版上是對的
        self.assertFalse(any(part(out, m).ok for m in ("m1", "m2", "m3")))   # 一般的一行，三個壞版本都拆得對

    def test_bear_six_cases_without_a_fullwidth_space_let_m1_slip(self):
        out = cases(BEAR6)
        self.assertTrue(part(out, "count").ok and part(out, "wheat").ok)
        self.assertEqual(part(out, "m2").note, "被第 3 行抓到")
        self.assertEqual(part(out, "m3").note, "被第 2 行抓到")
        self.assertFalse(part(out, "m1").ok)
        self.assertIn("全形空白", part(out, "m1").detail)
        self.assertIn("你的案例抓到 2 個壞版本，還有 1 個溜過去：", out.summaries)
        self.assertIn("  ・品項和金額中間是全形空白（中文輸入法打的空白）", out.summaries)

    def test_fullwidth_only_at_the_ends_does_not_catch_m1(self):
        """strip() 會拿掉前後的全形空白：全形空白要在品項和金額「中間」才抓得到 split(" ") 那一版。"""
        out = cases(BEAR6 + f'"{FW}早餐 65元{FW}" -> "早餐", 65\n')
        self.assertFalse(part(out, "m1").ok)
        out = cases(BEAR6 + f'"早餐{FW}65元" -> "早餐", 65\n')
        self.assertTrue(part(out, "m1").ok)
        self.assertEqual(part(out, "m1").note, "被第 7 行抓到")

    def test_escape_u3000_in_the_file_works_like_a_typed_fullwidth_space(self):
        out = cases(BEAR6 + '"早餐\\u300065元" -> "早餐", 65\n')
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_wrong_amount_shows_what_the_reference_splits(self):
        out = cases('"咖啡 85" -> "咖啡", 8\n')
        r = part(out, "wheat")
        self.assertFalse(r.ok)
        self.assertIn('split_item("咖啡 85") 正確版拆出來是 "咖啡", 85，你寫的是 "咖啡", 8', r.detail)
        out = cases('" 早餐 65元 " -> " 早餐", 65\n')   # 以為前面的空白會留著
        self.assertIn('正確版拆出來是 "早餐", 65', part(out, "wheat").detail)

    def test_list_parentheses_and_ideographic_comma_are_fine(self):
        out = cases('"午餐 120元" -> ["午餐", 120]\n"咖啡 85" -> ("咖啡", 85)\n"午餐   120元" -> "午餐"、120\n'
                    f'"午餐{FW}120元" -> "午餐",120\n" 早餐 65元 " -> "早餐", 65\n"飲料 50" -> "飲料", 50\n')
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_beginner_mistakes_get_plain_messages(self):
        for text, want in (('"午餐 120元" "午餐", 120\n', "少了箭頭"),
                           ('午餐 120元 -> "午餐", 120\n', "前後要加引號"),
                           ('"午餐 120元" -> 午餐, 120\n', "品項是文字，要加引號"),
                           ('"午餐 120元" -> "午餐", "120"\n', "有引號，是文字"),
                           ('"午餐 120元" -> "午餐", 120元\n', "不寫「元」"),
                           ('"午餐 120元" -> "午餐", 120.0\n', "有小數點"),
                           ('"午餐 120元" -> "午餐"\n', "寫了 1 個值"),
                           ('"午餐 120元" -> 120, "午餐"\n', "品項 120 不是文字"),
                           ('「午餐 120元」 -> "午餐", 120\n', "中文的引號")):
            out = cases(text)
            self.assertFalse(any(r.ok for r in out.results), text)
            self.assertIn(want, part(out, "count").detail, text)

    def test_crlf_fullwidth_arrow_and_comments_are_fine(self):
        out = cases(("# 我的案例\n\n" + TEACHER.replace('"咖啡 85" ->', '"咖啡 85" →') + "\n# 寫完了\n").replace("\n", "\r\n"))
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_one_four_ints_flag_is_untouched(self):
        """1-4 的 expect_ints（三個整數）照舊：expect_tuple 只對 1-5 生效。"""
        les = grader.load_lesson("1-4", COURSE)
        self.assertNotIn("expect_tuple", next(c for c in les.checks if c["id"] == "r3"))


class OtherChecks(unittest.TestCase):
    def setUp(self):
        start()

    def test_receipt_reference_passes_and_start_does_not(self):
        r = ev(["receipt"]).results[0]
        self.assertFalse(r.ok)
        shutil.copy(D / "reference" / "receipt.py", L / "lessons" / LID / "receipt.py")
        r = ev(["receipt"]).results[0]
        self.assertTrue(r.ok, r.detail)

    def test_receipt_without_thousands_comma_shows_the_hint(self):
        src = (D / "reference" / "receipt.py").read_text(encoding="utf-8")
        write(L / "lessons" / LID / "receipt.py", src.replace("{amount:,}", "{amount}"))
        r = ev(["receipt"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("1280元", r.detail)
        self.assertIn("{amount:,}", r.detail)

    def test_guess_answers(self):
        answer("guess.txt", ["2", "5", "12", "2026", "25", "52-21-6202", "85", "true"])
        out = ev(["guess"])
        self.assertEqual([r.ok for r in out.results], [True] * 8, [r.detail for r in out.results])
        answer("guess.txt", ["0", "2", "12-", "2026-", "-25", "2026-12-25", "85元", "False"])
        out = ev(["guess"])
        self.assertEqual([r.ok for r in out.results], [False] * 8)
        self.assertIn("之前", out.results[2].detail)

    def test_ai_quiz_answers(self):
        answer("ai_quiz.txt", ["第 4 題", "21", "b"])
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [True] * 3, [r.detail for r in out.results])
        answer("ai_quiz.txt", ["5", "2", "A"])
        out = ev(["ai"])
        self.assertEqual([r.ok for r in out.results], [False] * 3)

    def test_full_run_through_check_py(self):
        """check.py 1-05（課號補 0 也認得）：全對 17 題。"""
        home = fresh_dir("l15_home")
        env = make_env(home, now="2026-11-15T20:00:00+08:00")
        r = run_check(["setup", str(L)], env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_check(["start", "1-05"], env, stdin="")
        self.assertIn("uv run check.py 1-5", r.stdout)
        work = L / "lessons" / LID
        shutil.copy(D / "reference" / "receipt.py", work / "receipt.py")
        write(work / "cases.txt", TEACHER)
        answer("guess.txt", ["2", "5", "12", "2026", "25", "52-21-6202", "85", "True"])
        answer("ai_quiz.txt", ["4", "21", "B"])
        r = run_check(["1-05", "--predict", "16", "--no-review"], env)
        self.assertIn("17／17", r.stdout, r.stdout + r.stderr)
        self.assertIn("你的案例把 3 個壞版本全部抓到了。", r.stdout)


if __name__ == "__main__":
    unittest.main()
