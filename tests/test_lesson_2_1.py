"""2-1〈開 GitHub 帳號，第一次讓 AI 碰你的專案〉：作業與 check 的回歸測試（每課自己一個測試檔，不改 test_regressions.py）。

grader 加的東西（只對寫了它的題目生效）：run 的 exact_spaces（對齊的報表，行內空格要一模一樣）、
git_commits 的 email_suffix（git 的信箱是 GitHub 的 noreply 信箱）與 saved_before（存檔點裡找得到 report.py 原本的樣子＝交辦前先存檔）。
第①圈 expected.txt 用 1-1 的 chaff expected_text；noreply 信箱用 either（先不開帳號的寫 account.md）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄；帳本的 git 設定只寫在測試帳本自己的 .git/config。需要 uv 和 git。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, git, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l201"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "2-1"
D = COURSE / "lessons" / LID
NOREPLY = "12345678+plusform-bear@users.noreply.github.com"
RIGHT = ["A", "B", "C", "A"]


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
    return (D / "reference" / name).read_text(encoding="utf-8")


def mutant(name: str) -> str:
    return (D / "mutants" / name).read_text(encoding="utf-8")


def ev(ids: list[str], ledger: Path | None = L) -> grader.Outcome:
    les = grader.load_lesson(LID, COURSE)
    return grader.evaluate(les, ledger, only=[c for c in les.checks if c["id"] in ids])


def answer(name: str, answers: list[str]) -> None:
    p = mine(name)
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def fill(name: str, values: dict[str, str]) -> None:
    p = mine(name)
    out = []
    for ln in p.read_text(encoding="utf-8").splitlines():
        hit = next((k for k in values if ln.startswith(k)), None)
        out.append(ln + values[hit] if hit else ln)
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def expected_text(lines: list[str]) -> None:
    head = [ln for ln in mine("expected.txt").read_text(encoding="utf-8").splitlines() if ln.startswith("#")]
    write(mine("expected.txt"), "\n".join(head + lines) + "\n")


TEACHER = (D / "answers" / "expected.txt").read_text(encoding="utf-8").splitlines()


def set_email(addr: str) -> None:
    git(L, "config", "user.email", addr)   # 只寫測試帳本的 .git/config（蓋過 --global）


def fresh_repo() -> None:
    if (L / ".git").exists():
        shutil.rmtree(L / ".git")
    git(L, "init", "-q")
    set_email("bear@example.com")
    git(L, "add", "-A")
    git(L, "commit", "-q", "-m", "第一個存檔點")


def save(msg: str) -> None:
    git(L, "add", "-A")
    git(L, "commit", "-q", "--allow-empty", "-m", msg)


def setUpModule():
    if UV is None or shutil.which("git") is None:
        raise unittest.SkipTest("需要 uv 和 git")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Basics(unittest.TestCase):
    def test_lesson_id_forms(self):
        course = grader.course_info(COURSE)
        for raw in ("2-1", "2-01", "２－１"):
            self.assertEqual(grader.normalize_id(raw, course), "2-1")
        self.assertIn("2-1", grader.available_lessons(COURSE))

    def test_reference_prints_teacher_expected(self):
        """正確版印出來的，就是老師手寫的 expected.txt（一行一行、連空格）。"""
        p = subprocess.run(["python3", "-I", "-B", str(D / "reference" / "report.py")], capture_output=True, text=True, check=True)
        self.assertEqual(p.stdout.splitlines(), TEACHER)
        spec = next(c for c in grader.load_lesson(LID, COURSE).checks if c["id"] == "report")
        self.assertEqual(spec["expect_exact"], TEACHER)

    def test_start_and_mutants_differ_from_reference(self):
        outs = {}
        for name, path in [("start", D / "start" / "report.py")] + [(m, D / "mutants" / f"report_{m}.py") for m in ("m1", "m2", "m3")]:
            outs[name] = subprocess.run(["python3", "-I", "-B", str(path)], capture_output=True, text=True, check=True).stdout.splitlines()
        self.assertEqual(outs["start"][1], "餐飲 1250 元")
        self.assertEqual(outs["m1"][2], "交通  320 元")      # 靠左
        self.assertEqual(outs["m2"][1], "餐飲   1250 元")    # 沒有千分位
        self.assertEqual(outs["m3"][5], "合計 2,145 元")     # 合計沒對齊
        for name, out in outs.items():
            self.assertNotEqual(out, TEACHER, name)
            self.assertEqual(len(out), 6, name)


class Expected(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_not_done(self):
        out = ev(["r1"])
        self.assertFalse(all(r.ok for r in out.results))

    def test_teacher_passes(self):
        expected_text(TEACHER)
        out = ev(["r1"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_left_aligned_numbers_are_wrong(self):
        """學員以為「空兩格」就好：短的金額前面沒補空格，跟正確版不一樣（也就抓不到 m1）。"""
        expected_text(["11 月月報", "餐飲  1,250 元", "交通  320 元", "娛樂  480 元", "其他  95 元", "合計  2,145 元"])
        out = ev(["r1"])
        self.assertFalse(all(r.ok for r in out.results))

    def test_one_space_off(self):
        """其他那一行少一個空格：差一格也不行。"""
        lines = list(TEACHER)
        lines[4] = "其他    95 元"
        expected_text(lines)
        out = ev(["r1"])
        self.assertFalse(all(r.ok for r in out.results))

    def test_fullwidth_space_counts_as_one(self):
        """全形空白（NFKC 會變成半形）照一格算；行尾多打的空白不算。"""
        lines = [ln.replace("  ", "　 ", 1) if k == 1 else ln for k, ln in enumerate(TEACHER)]
        lines[3] += "   "
        expected_text(lines)
        out = ev(["r1"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])


class Email(unittest.TestCase):
    def setUp(self):
        start()
        fresh_repo()

    def tearDown(self):
        set_email("bear@example.com")

    def test_old_email_fails_with_both_ways(self):
        out = ev(["email"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("noreply", out.results[0].detail)
        self.assertIn("account.md", out.results[0].detail)

    def test_noreply_passes(self):
        set_email(NOREPLY)
        out = ev(["email"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)
        self.assertIn("noreply", out.results[0].note)

    def test_noreply_uppercase_domain_ok(self):
        set_email("12345678+plusform-bear@Users.NoReply.GitHub.com")
        self.assertTrue(ev(["email"]).results[0].ok)

    def test_lookalike_domain_fails(self):
        """自己拼的、不是 GitHub 給的網域（noreply.github.com.tw）不算。"""
        set_email("bear@users.noreply.github.com.tw")
        self.assertFalse(ev(["email"]).results[0].ok)

    def test_no_account_path(self):
        """先不開帳號：account.md 兩個標籤寫了就過（走第二條路）。"""
        fill("account.md", {"先不開帳號，因為：": "還不想留信箱", "第③圈改用：": "家教的聊天版，寫好再貼上"})
        out = ev(["email"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_no_account_half_filled(self):
        fill("account.md", {"先不開帳號，因為：": "還不想留信箱"})
        out = ev(["email"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("第③圈改用", out.results[0].detail)

    def test_not_a_repo(self):
        shutil.rmtree(L / ".git")
        out = ev(["email"])
        self.assertFalse(out.results[0].ok)
        fresh_repo()


class Commands(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("commands.txt", RIGHT)
        out = ev(["commands"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(len(out.results), 4)

    def test_approve_everything(self):
        """什麼都按同意（裝套件、丟掉改動、刪檔）：後三題都錯。"""
        answer("commands.txt", ["A", "A", "A", "B"])
        out = ev(["commands"])
        self.assertEqual([r.ok for r in out.results], [True, False, False, False])

    def test_two_letters_not_accepted(self):
        answer("commands.txt", ["A", "B 或 C", "C", "A"])
        out = ev(["commands"])
        self.assertFalse(out.results[1].ok)

    def test_key_letters_spread(self):
        key = json.loads((D / "answers" / "commands.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"] for q in key["questions"]], [[x] for x in RIGHT])


class Saved(unittest.TestCase):
    """交辦前先存檔：存檔點裡要有 report.py 原本的樣子；收下的版本也要存進存檔點。"""

    def setUp(self):
        start()
        if (L / ".git").exists():
            shutil.rmtree(L / ".git")
        git(L, "init", "-q")
        set_email("bear@example.com")

    def test_saved_then_kept_and_saved(self):
        save("交辦前")
        write(mine("report.py"), ref("report.py"))
        save("報表對齊")
        out = ev(["saved"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_never_saved_original(self):
        """沒存檔就讓 AI 改：存檔點裡只有改過的 report.py。"""
        write(mine("report.py"), ref("report.py"))
        save("報表對齊")
        save("再一個")
        out = ev(["saved"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("原本的樣子", out.results[0].detail)

    def test_kept_but_not_saved(self):
        save("交辦前")
        save("空的存檔點")
        write(mine("report.py"), ref("report.py"))
        out = ev(["saved"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("還沒按存檔點", out.results[0].detail)

    def test_crlf_and_trailing_spaces_still_original(self):
        """Windows 換行、行尾空白不算改過：存的還是原本的樣子。"""
        write(mine("report.py"), (D / "start" / "report.py").read_text(encoding="utf-8").replace("\n", "  \r\n"))
        save("交辦前")
        write(mine("report.py"), ref("report.py"))
        save("報表對齊")
        self.assertTrue(ev(["saved"]).results[0].ok)

    def test_only_one_save_point(self):
        save("交辦前")
        out = ev(["saved"])
        self.assertFalse(out.results[0].ok)
        self.assertIn("至少 2 個", out.results[0].detail)


class Report(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_fails(self):
        out = ev(["report"])
        self.assertFalse(out.results[0].ok)

    def test_reference_passes(self):
        write(mine("report.py"), ref("report.py"))
        out = ev(["report"])
        self.assertTrue(out.results[0].ok, out.results[0].detail)

    def test_mutants_fail_and_point_to_line(self):
        for m, line in (("m1", 3), ("m2", 2), ("m3", 6)):
            write(mine("report.py"), mutant(f"report_{m}.py"))
            r = ev(["report"]).results[0]
            self.assertFalse(r.ok, m)
            self.assertIn(f"第 {line} 行應該是", r.detail, m)
            self.assertIn("空格的數目也要一樣", r.detail, m)

    def test_loose_compare_would_have_passed_m1(self):
        """一般的 expect_exact 會把連續空白併成一個：m1（金額靠左）在舊的比法下會被當成對的，所以這題要 exact_spaces。"""
        out = subprocess.run(["python3", "-I", "-B", str(D / "mutants" / "report_m1.py")], capture_output=True, text=True, check=True).stdout
        self.assertEqual(grader.output_lines(out), grader.output_lines("\n".join(TEACHER)))

    def test_extra_line(self):
        write(mine("report.py"), ref("report.py") + 'print("（以上）")\n')
        r = ev(["report"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("多印了第 7 行", r.detail)

    def test_trailing_spaces_ok(self):
        write(mine("report.py"), ref("report.py").replace(' 元")', ' 元  ")'))
        self.assertTrue(ev(["report"]).results[0].ok)


class Decision(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_fails(self):
        self.assertFalse(ev(["decision"]).results[0].ok)

    def test_filled_passes(self):
        fill("decision.md", {"它要執行的指令：": "uv run lessons/2-1/report.py", "我按了同意還是拒絕：": "同意",
                             "diff 改了哪幾行：": "最後三行 print", "check 的結果：": "全過", "收不收，為什麼：": "收，跟 expected.txt 一樣"})
        self.assertTrue(ev(["decision"]).results[0].ok)


class Whole(unittest.TestCase):
    def test_all_right(self):
        start()
        if (L / ".git").exists():
            shutil.rmtree(L / ".git")
        git(L, "init", "-q")
        set_email(NOREPLY)
        expected_text(TEACHER)
        answer("commands.txt", RIGHT)
        fill("decision.md", {"它要執行的指令：": "uv run", "我按了同意還是拒絕：": "同意", "diff 改了哪幾行：": "三行",
                             "check 的結果：": "全過", "收不收，為什麼：": "收下"})
        save("交辦前")
        write(mine("report.py"), ref("report.py"))
        save("報表對齊")
        les = grader.load_lesson(LID, COURSE)
        out = grader.evaluate(les, L)
        bad = [(r.id, r.detail) for r in out.results if not r.ok]
        self.assertEqual(bad, [])
        self.assertEqual(len(out.results), 5 + 1 + 4 + 1 + 1 + 1)   # 第一圈 5＋1、第二圈 4、第三圈 3
        set_email("bear@example.com")


if __name__ == "__main__":
    unittest.main()
