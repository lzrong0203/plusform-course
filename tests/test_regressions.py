"""三份審查的必修，每一條各一個回歸測試（修好以前會失敗，修好以後要一直綠）。

編號：B＝新手實測、C＝程式碼審查（破壞性測試，原本在審查者的 scratch 裡）、P＝跟總企劃對照。
重複的必修（編碼、Windows 換行、老師的測試指令）共用同一個測試，名字裡兩個編號都寫。

全部寫在 PLUSFORM_TEST_WS 底下（假的家目錄、假的帳本、課程副本），不寫課程資料夾、不寫真的家目錄。
需要 uv（帳本是真的 uv 專案）；部分需要 git、bash、pgrep。
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
import unittest
import uuid
from pathlib import Path
from unittest import mock

from _support import COURSE, UV, WS, fresh_dir, git, make_env, run_check, uv_ledger

import check  # noqa: E402
import concept_map  # noqa: E402
from engine import grader, vshell  # noqa: E402

REG = WS / "reg"
L = REG / "ledger 帳本"  # 路徑有空白和中文
NOW1 = "2026-11-08T21:00:00+08:00"
NOW2 = "2026-11-09T20:00:00+08:00"


def write(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode(encoding))


def start(lid: str, ledger: Path = L) -> Path:
    """把這課的起點檔重新複製一份到帳本（每個測試從乾淨的起點開始）。"""
    src = COURSE / "lessons" / lid / "start"
    dest = ledger / "lessons" / lid
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return dest


def fill(path: Path, answers: list[str]) -> None:
    it = iter(answers)
    lines = [("答：" + next(it)) if ln.strip().startswith("答：") else ln for ln in path.read_text(encoding="utf-8").splitlines()]
    write(path, "\n".join(lines) + "\n")


def lesson(lid: str, root: Path = COURSE) -> grader.Lesson:
    return grader.load_lesson(lid, root)


def ev(lid: str, ids: list[str] | None = None, types: list[str] | None = None, ledger: Path | None = L,
       env: grader.Env | None = None, overrides: dict | None = None, root: Path = COURSE) -> grader.Outcome:
    les = lesson(lid, root)
    only = [c for c in les.checks if (ids is None or c["id"] in ids) and (types is None or c["type"] in types)]
    return grader.evaluate(les, ledger, env=env, overrides=overrides, only=only)


def part(out: grader.Outcome, suffix: str) -> grader.Result:
    return next(r for r in out.results if r.id.rsplit("-", 1)[-1] == suffix)


def copy_course(name: str) -> Path:
    dest = REG / "courses" / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(COURSE, dest, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return dest


def validate(root: Path, *lessons: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-B", str(COURSE / "tools" / "validate_lesson.py"), "--root", str(root), "--no-env", *lessons]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)


def fake_student(name: str, lessons: dict, attempts: list | None = None, reviews: list | None = None):
    """不用 uv 的假學員：只有設定檔和 .check 紀錄（回顧題、status 用）。"""
    home = fresh_dir(f"reg_{name}")
    ledger = home / "code" / "ledger"
    (ledger / ".check").mkdir(parents=True)
    cfg = home / ".config" / "plusform-course"
    cfg.mkdir(parents=True)
    (cfg / "config.json").write_text(json.dumps({"ledger": str(ledger)}), encoding="utf-8")
    (ledger / ".check" / "progress.json").write_text(json.dumps({"version": 1, "lessons": lessons, "frontier": -1}),
                                                       encoding="utf-8")
    for fname, rows in (("attempts", attempts or []), ("reviews", reviews or [])):
        (ledger / ".check" / f"{fname}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                                                            encoding="utf-8")
    return home, ledger


def passed_on(day: str) -> dict:
    return {"first_run": day, "first_pass": day, "runs": 1}


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    REG.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


# ====================================================================
# B：新手實測
# ====================================================================

class Beginner(unittest.TestCase):
    def test_B01_doctor_does_not_print_the_reference_output(self):
        work = start("0-5")
        write(work / "doctor_expected.txt", "Python 版本：3.13.13\n在帳本的環境裡：是\n用的是系統 Python：否\n")
        wheat = part(ev("0-5", ids=["r3"]), "wheat")
        self.assertFalse(wheat.ok)
        self.assertNotIn("正確版在你的電腦上印的是", wheat.detail)
        for leak in ("在帳本的環境裡:是", "用的是系統 Python:否", "Python 版本:3.13\n"):
            self.assertNotIn(leak, wheat.detail)
        self.assertIn("印的不是這個答案", wheat.detail)
        self.assertIn("版本寫兩段數字", wheat.detail)

    def test_B02_doctor_lines_ignore_spaces_and_colon_width(self):
        work = start("0-5")
        write(work / "doctor_expected.txt", "Python版本：3.13\n在帳本的環境裡： 是\n用的是系統 Python:否\n")
        out = ev("0-5", ids=["r3"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results if not r.ok])
        write(work / "doctor_expected.txt", "Python 的版本：3.13\n在帳本的環境裡：是\n用的是系統 Python：否\n")
        wheat = part(ev("0-5", ids=["r3"]), "wheat")
        self.assertIn("冒號前面的字被改到了，只要改「？」就好", wheat.detail)
        self.assertIn("「Python 版本」", wheat.detail)
        self.assertNotIn("3.13」", wheat.detail.split("冒號前面照原本的寫")[-1])

    def test_B03_answer_title_quotes_the_error_and_says_which_file(self):
        start("0-5")
        r = ev("0-5", ids=["err"]).results[0]
        self.assertEqual(r.desc, "對答第 1 題（錯誤訊息「zsh: command not found: uv」）")
        self.assertIn("還沒作答：打開帳本裡的 lessons/0-5/error_match.txt", r.detail)
        self.assertIn("A、B 或 C", r.detail)
        self.assertNotIn("zsh", r.detail)

    def test_B04_choice_with_copied_text_counts(self):
        work = start("0-5")
        for answers in (["B. PATH 還沒更新", "（A）", "C、之前亂加 sudo"],
                        ["PATH 還沒更新，終端機找不到剛裝好的指令", "a", "c"]):
            fill(work / "error_match.txt", answers)
            out = ev("0-5", ids=["err"])
            self.assertTrue(all(r.ok for r in out.results), (answers, [r.detail for r in out.results if not r.ok]))
        fill(work / "error_match.txt", ["我不知道", "A", "C"])
        r = ev("0-5", ids=["err"]).results[0]
        self.assertIn("只要寫一個字母", r.detail)
        self.assertNotIn("不對", r.detail)

    def test_B05_missing_main_py_points_to_uv_init(self):
        pkg = uv_ledger(REG / "pkg_ledger", package=True)
        uvp, main = ev("0-5", ids=["uv-project", "main"], ledger=pkg).results
        self.assertTrue(uvp.ok)
        self.assertNotIn("先不用管", uvp.note)
        self.assertIn("rm -r src", uvp.note)
        self.assertIn("uv init --no-package --vcs none", main.detail)
        self.assertNotIn("start 0-5", main.detail)
        plain = REG / "no_main_ledger"
        if plain.exists():
            shutil.rmtree(plain)
        shutil.copytree(L, plain, ignore=shutil.ignore_patterns(".venv", "lessons", ".check"))
        (plain / "main.py").unlink()
        main = ev("0-5", ids=["main"], ledger=plain).results[0]
        self.assertIn("main.py 是 uv init 建的", main.detail)
        self.assertNotIn("start 0-5", main.detail)

    def test_B06_running_check_from_the_wrong_folder_is_explained(self):
        root = (COURSE / "README.md").read_text(encoding="utf-8")
        self.assertIn("Failed to spawn: check.py", root)
        self.assertIn("uv run ~/code/plusform-course/check.py", root)
        r19 = (COURSE / "lessons/1-9/README.md").read_text(encoding="utf-8")
        block = r19.split("uv run lessons/1-9/checks_bmi.py", 1)[1][:80]
        self.assertIn("cd ~/code/plusform-course", block)
        self.assertIn("Failed to spawn", r19)
        home = fresh_dir("reg_b06_home")
        r = subprocess.run([UV, "run", "--quiet", str(COURSE / "check.py"), "--help"], cwd=L, env=make_env(home),
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_B07_old_python_gets_a_plain_message(self):
        for rel in ("check.py", "concept_map.py"):
            ast.parse((COURSE / rel).read_text(encoding="utf-8"), feature_version=(3, 9))
        old = Path("/usr/bin/python3")
        if not old.is_file():
            self.skipTest("這台電腦沒有內建的 python3")
        ver = subprocess.run([str(old), "-c", "import sys; print(sys.version_info[:2] < (3, 13))"],
                             capture_output=True, text=True).stdout.strip()
        if ver != "True":
            self.skipTest("內建的 python3 已經是 3.13 以上")
        r = subprocess.run([str(old), "-B", str(COURSE / "check.py"), "0-5"], capture_output=True, text=True,
                           encoding="utf-8", cwd=COURSE, env=make_env(fresh_dir("reg_b07_home")))
        self.assertEqual(r.returncode, 2)
        self.assertIn("uv run check.py", r.stdout)
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_B08_wrong_review_answer_shows_the_answer_and_why(self):
        home, _ledger = fake_student("b08", {"0-5": passed_on(NOW1), "1-9": passed_on(NOW1)})
        r = run_check(["review", "0-5:r2", "python3", "main.py"], make_env(home, NOW2))
        self.assertEqual(r.returncode, 1)
        self.assertIn("✗ 這題先算錯，下次會換一題再問你。", r.stdout)
        self.assertIn("正確答案：uv run main.py", r.stdout)
        self.assertIn("用 uv run，才會用帳本自己的 Python 3.13", r.stdout)
        self.assertNotIn("。 下次", r.stdout)

    def test_B09_review_days_count_as_practice(self):
        home, _ledger = fake_student(
            "b09", {"0-5": passed_on(NOW1), "1-9": passed_on(NOW1)},
            attempts=[{"time": NOW1, "lesson": "1-9", "predicted": None, "passed": 1, "total": 1}],
            reviews=[{"time": NOW2, "lesson": "0-5", "slot": 2, "qid": "r1", "answer": "A", "correct": True, "leaf": True}])
        r = run_check(["status"], make_env(home, NOW2))
        self.assertIn("練習天數：2 天", r.stdout)
        self.assertIn("技能樹的葉子：1 片", r.stdout)

    def test_B10_lesson_0_5_readme_is_followable(self):
        text = (COURSE / "lessons/0-5/README.md").read_text(encoding="utf-8")
        for must in ("https://docs.astral.sh/uv/", "curl -LsSf https://astral.sh/uv/install.sh | sh",
                     "mv ~/Downloads/plusform-course-main ~/code/plusform-course", "open -e", "已經裝好了"):
            self.assertIn(must, text)
        after = json.loads((COURSE / "lessons/0-5/lesson.json").read_text(encoding="utf-8"))["after_start"]
        self.assertIn("error_match.txt", after)
        self.assertIn("doctor_expected.txt", after)

    def test_B11_ratio_compared_with_80_gets_the_right_hint(self):
        work = start("1-9")
        src = (COURSE / "lessons/1-9/reference/budget_light.py").read_text(encoding="utf-8")
        write(work / "budget_light.py", src.replace("ratio < 0.8", "ratio < 80").replace("ratio <= 1", "ratio <= 100"))
        out = ev("1-9", types=["run"])
        first = next(r for r in out.results if not r.ok)
        self.assertIn("要寫 0.8，不是 80", first.detail)
        self.assertIn("0.8（不是 80）", (COURSE / "lessons/1-9/start/budget_light.py").read_text(encoding="utf-8"))

    def test_B12_extra_input_is_explained_in_chinese(self):
        work = start("1-9")
        src = (COURSE / "lessons/1-9/reference/budget_light.py").read_text(encoding="utf-8")
        write(work / "budget_light.py", src.replace("ratio = spent / budget", 'name = input("你的名字？")\nratio = spent / budget'))
        r = ev("1-9", ids=["light-1"]).results[0]
        self.assertIn("你的程式要的輸入比這題給的多（這題只給了：500、1000）", r.detail)
        self.assertIn("多寫了一個 input()", r.detail)
        self.assertNotIn("EOFError: EOF when reading a line", r.detail)
        write(work / "budget_light.py", "a = input()\nb = input()\nwhile True:\n    pass\n")
        r = ev("1-9", ids=["light-1"], env=grader.Env(L, timeout=2)).results[0]
        self.assertIn("無窮迴圈", r.detail)
        self.assertNotIn("input()", r.detail)


# ====================================================================
# C：程式碼審查（破壞性）
# ====================================================================

def pgrep(marker: str) -> list[str]:
    return subprocess.run(["pgrep", "-f", marker], capture_output=True, text=True).stdout.split()


@unittest.skipIf(os.name == "nt" or shutil.which("pgrep") is None, "要 pgrep")
class Processes(unittest.TestCase):
    def test_C01_timeout_kills_the_whole_process_tree_and_does_not_wait_again(self):
        marker = f"plusform_reg_{uuid.uuid4().hex[:10]}"
        prog = REG / f"{marker}.py"
        write(prog, textwrap.dedent(f"""
            import subprocess, sys
            a = input()
            b = input()
            subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)  # {marker}"])
            while True:
                pass
        """))
        try:
            t0 = time.monotonic()
            out = ev("1-9", types=["run"], env=grader.Env(L, timeout=2), overrides={"lessons/1-9/budget_light.py": prog})
            spent = time.monotonic() - t0
            self.assertTrue(all(not r.ok for r in out.results))
            self.assertIn("跑了 2 秒還沒結束", out.results[0].detail)
            self.assertIn("同一支程式剛剛就", out.results[1].detail)
            self.assertLess(spent, 8, "同一支程式第一次跑不完以後，其他題不該再各等一次")
            time.sleep(0.5)
            self.assertEqual(pgrep(marker), [], "逾時之後還有學員的程式（或它開的子程序）在跑")
        finally:
            subprocess.run(["pkill", "-f", marker], capture_output=True)

    def test_C02_output_is_capped(self):
        prog = REG / "c02_flood.py"
        write(prog, "a = input()\nb = input()\nimport sys\nline = '綠燈' * 50 + '\\n'\nfor i in range(1_000_000):\n    sys.stdout.write(line)\n")
        probe = textwrap.dedent(f"""
            import sys, resource
            sys.dont_write_bytecode = True
            sys.path.insert(0, {str(COURSE)!r})
            from pathlib import Path
            from engine import grader
            les = grader.load_lesson("1-9")
            spec = [c for c in les.checks if c["id"] == "light-1"]
            out = grader.evaluate(les, Path({str(L)!r}), only=spec, overrides={{"lessons/1-9/budget_light.py": Path({str(prog)!r})}})
            print(out.results[0].detail.replace("\\n", " "))
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            print(rss // (1024 * 1024) if sys.platform == "darwin" else rss // 1024)
        """)
        r = subprocess.run([sys.executable, "-B", "-c", probe], capture_output=True, text=True, encoding="utf-8", timeout=120)
        lines = r.stdout.strip().splitlines()
        self.assertTrue(lines, r.stderr)
        self.assertIn("印了太多東西", lines[0])
        self.assertLess(int(lines[-1]), 300, "學員印了約 150 MB，check 這邊的記憶體不該跟著漲")
        # runner 裡（第③圈）學員的檢查狂印，也要停得下來
        work = start("1-9")
        write(work / "checks_bmi.py", "from bmi import bmi_level\nfor i in range(10**9):\n    print('x' * 100)\n"
                                      + 'assert bmi_level(16) == "過輕"\n' * 6)
        t0 = time.monotonic()
        wheat = part(ev("1-9", ids=["r3"]), "wheat")
        self.assertIn("印太多了", wheat.detail)
        self.assertLess(time.monotonic() - t0, 25)


class Encodings(unittest.TestCase):
    def test_C03_P08_bom_and_big5_files(self):
        work = start("1-9")
        teacher = (COURSE / "lessons/1-9/answers/checks_bmi.py").read_text(encoding="utf-8")
        with self.subTest("UTF-8 BOM 的 assert 檔"):
            write(work / "checks_bmi.py", "\ufeff" + teacher)
            out = ev("1-9", ids=["r3"])
            self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results if not r.ok][:1])
        with self.subTest("BOM＋CRLF 的路徑檢查"):
            tmp = REG / "c03_bom_checks.txt"
            write(tmp, "\ufeff# 我的檢查\r\nbudget/2026-11/food.txt\r\nbudget/todo_copy.txt\r\nnotes/todo.txt\r\n")
            out = ev("0-4", types=["chaff"], ledger=None, env=grader.Env(None, local=True),
                     overrides={"lessons/0-4/checks.txt": tmp})
            self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results if not r.ok][:1])
        with self.subTest("Big5 的 assert 檔：白話說明，不噴 Traceback"):
            write(work / "checks_bmi.py", teacher, encoding="big5")
            out = ev("1-9", ids=["r3"])
            self.assertFalse(out.results[0].ok)
            self.assertIn("不是用 UTF-8 存的", out.results[0].detail)
        with self.subTest("Big5 的作答檔"):
            w5 = start("0-5")
            write(w5 / "error_match.txt", (w5 / "error_match.txt").read_text(encoding="utf-8").replace("答：", "答：B", 1),
                  encoding="big5")
            r = ev("0-5", ids=["err"]).results[0]
            self.assertIn("不是用 UTF-8 存的", r.detail)
        with self.subTest("Big5 的程式"):
            src = (COURSE / "lessons/1-9/reference/budget_light.py").read_text(encoding="utf-8")
            write(work / "budget_light.py", src, encoding="big5")
            r = ev("1-9", ids=["light-1"]).results[0]
            self.assertIn("不是用 UTF-8 存的", r.detail)
        with self.subTest("整支 check.py 也不噴 Traceback"):
            home = fresh_dir("reg_c03_home")
            env = make_env(home)
            run_check(["setup", str(L)], env)
            r = run_check(["1-9", "--predict", "1", "--no-review"], env)
            self.assertNotIn("Traceback", r.stdout + r.stderr)


class SpecialMarks(unittest.TestCase):
    def test_C04_known_crash_is_checked_by_really_running_the_reference(self):
        work = start("1-9")
        base = (COURSE / "lessons/1-9/answers/checks_bmi.py").read_text(encoding="utf-8")
        for call in ("bmi_level()", "bmi_level(None)", "bmi_level([20])"):
            with self.subTest(call=call):
                write(work / "checks_bmi.py", base + f'assert {call} == "過輕"  # 已知會當掉\n')
                marks = [r for r in ev("1-9", ids=["r3"]).results if r.special]
                self.assertTrue(marks and marks[0].ok, marks[0].detail if marks else "沒有標記結果")
                self.assertIn("正確版跑這一行真的會當掉", marks[0].note)
        with self.subTest("註解只是提到，不算標記"):
            write(work / "checks_bmi.py", base.replace('assert bmi_level(24) == "過重"',
                                                       'assert bmi_level(24) == "過重"  # 這條不是已知會當掉，是邊界'))
            out = ev("1-9", ids=["r3"])
            self.assertFalse(any(r.special for r in out.results))
            self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results if not r.ok][:1])


class VShellFailClosed(unittest.TestCase):
    def test_C05_unsupported_shell_syntax_is_never_called_safe(self):
        c = COURSE / "lessons/0-C"
        ref = (c / "reference/make_v0.sh").read_text(encoding="utf-8")
        tmp = REG / "c05_make_v0.sh"
        for line in ('rm -rf "$HOME/code/ledger/lessons/0-4"', "rm -rf $PWD/../0-4", "rm -rf $(pwd)/../0-4",
                     "rm -rf `pwd`/../0-4", "rm -rf ~bear/code/ledger/lessons/0-4", "rm -rf ../0-[4]",
                     "mkdir -p v0/{data,notes}", 'echo "" > v0/notes/budget.txt'):
            with self.subTest(line=line):
                write(tmp, ref + line + "\n")
                r = ev("0-C", ids=["safe"], ledger=None, env=grader.Env(None, local=True),
                       overrides={"lessons/0-C/make_v0.sh": tmp}).results[0]
                self.assertFalse(r.ok, f"{line} 被判成安全")
                self.assertIn("模擬器看不懂的寫法", r.detail)
                self.assertIsNotNone(vshell.unsupported(line))
        self.assertIsNone(vshell.unsupported('echo "帳本 v0 的資料夾建好了"'))
        self.assertIsNone(vshell.unsupported("echo '$HOME 不會展開'"))


class Isolation(unittest.TestCase):
    def test_C06_each_version_runs_alone(self):
        work = start("1-9")
        teacher = (COURSE / "lessons/1-9/answers/checks_bmi.py").read_text(encoding="utf-8")
        with self.subTest("壞版本無窮迴圈：算被抓到，正確版不被拖累"):
            root = copy_course("c06_loop")
            m1 = root / "lessons/1-9/mutants/bmi_m1.py"
            m1.write_text(m1.read_text(encoding="utf-8").replace(
                "    elif bmi > 24:", "    elif bmi == 24:\n        while True:\n            pass\n    elif bmi > 24:"), encoding="utf-8")
            out = ev("1-9", ids=["r3"], ledger=None, env=grader.Env(None, local=True, timeout=3), root=root,
                     overrides={"lessons/1-9/checks_bmi.py": root / "lessons/1-9/answers/checks_bmi.py"})
            self.assertTrue(part(out, "wheat").ok, part(out, "wheat").detail)
            self.assertTrue(part(out, "m1").ok)
            self.assertIn("卡住了", part(out, "m1").note)
        with self.subTest("版本之間不共用狀態"):
            write(work / "checks_bmi.py", "import os\n" + "assert 'SEEN' not in os.environ\n" * 6 + "os.environ['SEEN'] = '1'\n")
            out = ev("1-9", ids=["r3"])
            self.assertEqual([r.id for r in out.results if r.id.endswith(("m1", "m2", "m3")) and r.ok], [])
        with self.subTest("偽造的結果行不算數"):
            fake = json.dumps({"load_error": None, "setup_error": None, "asserts": []})
            write(work / "checks_bmi.py", "import sys\n" + "assert True\n" * 6 +
                  f"sys.__stdout__.write('\\n@@PLUSFORM@@@@result {fake}\\n')\n")
            out = ev("1-9", ids=["r3"])
            self.assertEqual([r.id for r in out.results if r.id.endswith(("m1", "m2", "m3")) and r.ok], [])
        write(work / "checks_bmi.py", teacher)


class Validator(unittest.TestCase):
    def run_edit(self, name, edit, lid="1-9"):
        root = copy_course(name)
        edit(root / "lessons" / lid)
        return validate(root, lid)

    def test_C07_validator_rejects_bad_mutants_and_bad_start_files(self):
        ref = (COURSE / "lessons/1-9/reference/bmi.py").read_text(encoding="utf-8")
        cases = {
            "語法錯誤的壞版本": lambda d: (d / "mutants/bmi_m1.py").write_text("def bmi_level(bmi)\n    return 1\n", encoding="utf-8"),
            "一載入就當掉的壞版本": lambda d: (d / "mutants/bmi_m1.py").write_text('x = int("abc")\n\n\n' + ref, encoding="utf-8"),
            "永遠答錯的壞版本": lambda d: (d / "mutants/bmi_m1.py").write_text('def bmi_level(bmi):\n    return "不知道"\n', encoding="utf-8"),
            "起點檔的範例在正確版上不成立": lambda d: (d / "start/checks_bmi.py").write_text(
                (d / "start/checks_bmi.py").read_text(encoding="utf-8").replace('bmi_level(16) == "過輕"', 'bmi_level(16) == "正常"'),
                encoding="utf-8"),
            "起點程式一開始就全過": lambda d: shutil.copy(d / "reference/budget_light.py", d / "start/budget_light.py"),
            "checks.json 壞掉": lambda d: (d / "tests/checks.json").write_text('{"checks": [{"type": "chaff"}]}', encoding="utf-8"),
        }
        expect = {
            "語法錯誤的壞版本": "語法錯誤",
            "一載入就當掉的壞版本": "一載入就當掉",
            "永遠答錯的壞版本": "一條都不成立",
            "起點檔的範例在正確版上不成立": "範例檢查在正確版上不成立",
            "起點程式一開始就全過": "一開始就通過全部",
            "checks.json 壞掉": "驗證時出了意外",
        }
        for i, (what, edit) in enumerate(cases.items()):
            with self.subTest(what):
                r = self.run_edit(f"c07_{i}", edit)
                self.assertEqual(r.returncode, 1, r.stdout[-600:])
                self.assertNotIn("Traceback", r.stdout + r.stderr)
                self.assertIn(expect[what], r.stdout)


class WindowsNewlines(unittest.TestCase):
    def test_C08_P09_crlf_scripts(self):
        ga = (COURSE / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("*.sh text eol=lf", ga)
        with self.subTest("start 複製 .sh 時換成 LF"):
            root = copy_course("c08_crlf")
            sh = root / "lessons/0-C/start/make_v0.sh"
            sh.write_bytes(sh.read_bytes().replace(b"\n", b"\r\n"))
            home, ledger = fake_student("c08", {})
            env = make_env(home)
            r = subprocess.run([sys.executable, "-B", str(root / "check.py"), "start", "lv0", "--predict", "1"],
                               capture_output=True, text=True, encoding="utf-8", env=env, cwd=root, timeout=120)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertNotIn(b"\r", (ledger / "lessons/0-C/make_v0.sh").read_bytes())
        with self.subTest("學員自己存成 CRLF：說清楚怎麼改"):
            tmp = REG / "c08_make.sh"
            tmp.write_bytes((COURSE / "lessons/0-C/reference/make_v0.sh").read_bytes().replace(b"\n", b"\r\n"))
            r = ev("0-C", ids=["safe"], ledger=None, env=grader.Env(None, local=True),
                   overrides={"lessons/0-C/make_v0.sh": tmp}).results[0]
            self.assertFalse(r.ok)
            self.assertIn("CRLF", r.detail)
        with self.subTest("bash 跑 CRLF 腳本建出的怪名字：說是換行的問題"):
            work = start("0-C")
            for name in ("data\r", "notes\r"):
                (work / "v0" / name).mkdir(parents=True, exist_ok=True)
            r = ev("0-C", ids=["ran"]).results[0]
            self.assertFalse(r.ok)
            self.assertIn("看不見字元", r.detail)
            shutil.rmtree(work / "v0")


class TeacherCommand(unittest.TestCase):
    def test_C09_P11_teacher_test_command_is_isolated(self):
        text = (COURSE / "README.md").read_text(encoding="utf-8")
        lines = [ln for ln in text.splitlines() if "unittest" in ln]
        self.assertTrue(lines)
        for ln in lines:
            self.assertIn("--no-project", ln)
            self.assertIn("-B", ln)
        self.assertIn("uv run tests/run_all.py", text)
        head = (COURSE / "tests/run_all.py").read_text(encoding="utf-8")
        self.assertTrue(head.startswith("# /// script"))
        self.assertIn("sys.dont_write_bytecode = True", head)


# ====================================================================
# P：跟總企劃對照
# ====================================================================

class PlanConformance(unittest.TestCase):
    def test_P01_lesson_1_9_students_only_call_bmi_level(self):
        les = lesson("1-9")
        self.assertFalse([c for c in les.checks if c["type"] == "call"], "1-9 不該要學員寫 bmi_level 再用 call 測")
        start_code = ast.dump(ast.parse((COURSE / "lessons/1-9/start/bmi.py").read_text(encoding="utf-8")))
        ref_code = ast.dump(ast.parse((COURSE / "lessons/1-9/reference/bmi.py").read_text(encoding="utf-8")))
        self.assertEqual(start_code, ref_code, "start/bmi.py 要是課程凍結的正確版")
        readme = (COURSE / "lessons/1-9/README.md").read_text(encoding="utf-8")
        self.assertNotIn("在課程寫好的外殼", readme)
        self.assertIn("你**不用寫它**", readme)
        concepts = (COURSE / "lessons/1-9/CONCEPTS.md").read_text(encoding="utf-8")
        self.assertRegex(concepts, r"函式外殼（例外：")

    def test_P02_lesson_1_9_has_trace_ai_review_and_judgment_card(self):
        les = lesson("1-9")
        ids = {c["id"]: c for c in les.checks}
        self.assertEqual(ids["trace"]["type"], "answers")
        self.assertEqual(ids["ai"]["type"], "answers")
        key = json.loads((COURSE / "lessons/1-9/answers/ai_review.json").read_text(encoding="utf-8"))
        self.assertTrue(6 <= len(key["questions"]) <= 8)
        rejected = [q for q in key["questions"] if "不採用" in q["accept"]]
        self.assertTrue(2 <= len(rejected) <= 4)  # a5（AI 說錯、查證後也可以不採用）兩種答案都收，所以最多 4 則
        self.assertTrue(any("dict" in q["title"] for q in rejected))
        for f in ("start/judgment_card.md", "answers/judgment_card_example.md"):
            self.assertTrue((COURSE / "lessons/1-9" / f).is_file(), f)
        self.assertIn("量表", (COURSE / "lessons/1-9/answers/judgment_card_example.md").read_text(encoding="utf-8"))
        work = start("1-9")
        fill(work / "trace.txt", ["過輕", "正常", "過重", "肥胖"])
        fill(work / "ai_review.txt", [q["accept"][0] for q in key["questions"]])
        out = ev("1-9", ids=["trace", "ai"])
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results if not r.ok])

    @unittest.skipIf(shutil.which("git") is None, "要 git")
    def test_P03_lesson_0_C_builds_ledger_v0_with_two_saves(self):
        les = lesson("0-C")
        by = {c["id"]: c for c in les.checks}
        self.assertEqual(by["main"]["file"], "main.py")
        self.assertEqual(by["saved"]["type"], "git_commits")
        self.assertEqual(by["saved"]["min"], 2)
        self.assertLess(les.meta["fast_minutes"], 10)
        self.assertEqual(les.meta["timed"]["rebuild"]["standard"], 10)
        g = REG / "p03_git_ledger"
        if g.exists():
            shutil.rmtree(g)
        g.mkdir(parents=True)
        (g / "main.py").write_text('print("Hello from ledger!")\n', encoding="utf-8")
        saved = lambda: ev("0-C", ids=["saved"], ledger=g).results[0]  # noqa: E731
        self.assertIn("帳本還不是 git 存放庫", saved().detail)
        git(g, "init", "--quiet")
        git(g, "add", "-A")
        git(g, "commit", "--quiet", "-m", "一")
        self.assertIn("帳本現在有 1 個存檔點", saved().detail)
        (g / "main.py").write_text((COURSE / "lessons/0-C/reference/main.py").read_text(encoding="utf-8"), encoding="utf-8")
        (g / "notes.txt").write_text("x", encoding="utf-8")
        git(g, "add", "notes.txt")
        git(g, "commit", "--quiet", "-m", "二")
        self.assertIn("main.py 改過之後還沒按存檔點", saved().detail)
        git(g, "add", "main.py")
        git(g, "commit", "--quiet", "-m", "三")
        self.assertTrue(saved().ok)
        work = start("0-C")
        for d in ("data/receipts", "notes", "practice"):
            (work / "rebuild" / d).mkdir(parents=True, exist_ok=True)
        for f in ("notes/todo.txt", "notes/hello_copy.txt", "practice/hello.txt", "practice/final.txt"):
            (work / "rebuild" / f).touch()
        r = ev("0-C", ids=["rebuild"]).results[0]
        self.assertTrue(r.ok, r.detail)
        self.assertIn("minutes", r.data)

    def test_P04_at_most_two_reviews_one_per_slot(self):
        lessons = {lid: passed_on(NOW1) for lid in ("0-4", "0-5", "0-C", "1-9")}
        home, ledger = fake_student("p04", lessons)
        with mock.patch.dict(os.environ, make_env(home, NOW2), clear=True):
            records = check.state.Records(ledger)
            due = check.due_reviews(records, current="1-9")
            self.assertEqual(len(due), 2)
            self.assertEqual([d["slot"] for d in due], [2, 5])
            self.assertGreater(len(check.review_candidates(records)), 2)
            order = ["0-4", "0-5", "a", "b", "c", "0-C", "d", "1-9"]
            fake = {"lessons": [{"id": x, "title": x} for x in order]}
            with mock.patch.object(check, "course", return_value=fake):
                due = check.due_reviews(records, current="1-9")
                self.assertEqual(due[0]["lesson"], "0-C", "2 課前那一題要先挑正好往前數第 2 課的")
                self.assertEqual(due[1]["lesson"], "0-4", "沒有正好 5 課前的，就挑積欠最久的")
        r = run_check(["status"], make_env(home, NOW2))
        self.assertIn("今天到期的回顧題：2 題", r.stdout)
        self.assertIn("題排隊", r.stdout)

    def test_P05_concepts_md_must_match_the_lesson_order(self):
        def drop_exceptions(d):
            p = d / "CONCEPTS.md"
            p.write_text(p.read_text(encoding="utf-8").replace("（例外：只跑不讀）", ""), encoding="utf-8")
        root = copy_course("p05_concepts")
        drop_exceptions(root / "lessons/0-5")
        r = validate(root, "0-5")
        self.assertEqual(r.returncode, 1)
        self.assertIn("要到 1-1 才教，比這課（0-5）晚", r.stdout)
        r = validate(COURSE, "0-5")
        self.assertIn("※ 例外：「模組與 import」（1-21 才教）", r.stdout)

    def test_P06_showcase_is_labelled_honestly(self):
        for rel in ("showcase/README.md", "README.md"):
            text = (COURSE / rel).read_text(encoding="utf-8")
            self.assertNotIn("挑選過的一次執行", text)
            self.assertNotIn("從幾次產出裡挑", text)
            self.assertIn("情境重現", text)

    def test_P07_showcase_only_uses_lv1_concepts(self):
        src = (COURSE / "showcase/ledger_app.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        mods = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        mods |= {(n.module or "").split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertFalse(mods & {"json", "os", "csv", "sqlite3"}, mods)
        self.assertEqual(concept_map.CONCEPTS["json"][1], "2-4")
        self.assertEqual(concept_map.CONCEPTS["environ"][1], "2-7")
        tags = {i.text.strip(): i.concepts for i in concept_map.analyze_source(
            "import json\nimport os\nx = os.environ['A']\ny = json.loads('1')\n")}
        self.assertIn("environ", tags["x = os.environ['A']"])
        self.assertIn("json", tags["y = json.loads('1')"])
        order = [x["id"] for x in grader.course_info(COURSE)["lessons"]]
        lv1 = set(order[: order.index("1-27") + 1])
        self.assertEqual(concept_map.progress(src, lv1).percent, 100)

    @unittest.skipIf(shutil.which("bash") is None, "要 bash")
    def test_P10_course_scripts_cannot_delete_student_work(self):
        self.assertFalse(list((COURSE / "lessons/0-4/start").glob("*.sh")), "0-4 的腳本只讀不跑，不該存成 .sh")
        for sh in (COURSE / "lessons").glob("*/start/*.sh"):
            for line in sh.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("rm "):
                    self.assertIn("保險箱", line, f"{sh} 會刪真的東西：{line}")
        fake = fresh_dir("reg_p10") / "ledger"
        (fake / "lessons/0-4").mkdir(parents=True)
        (fake / "lessons/0-4/checks.txt").write_text("我的作答", encoding="utf-8")
        (fake / "lessons/0-C").mkdir(parents=True)
        (fake / "main.py").write_text("print('hi')\n", encoding="utf-8")
        shutil.copy(COURSE / "lessons/0-C/start/make_v0.sh", fake / "lessons/0-C/make_v0.sh")
        shutil.copytree(COURSE / "lessons/0-C/start_outside", fake / "lessons", dirs_exist_ok=True)
        subprocess.run(["bash", "make_v0.sh"], cwd=fake / "lessons/0-C", capture_output=True, timeout=30)
        self.assertTrue((fake / "lessons/0-4/checks.txt").is_file(), "沒讀就跑，也不能刪到學員自己的作業")
        self.assertFalse((fake / "lessons/0-C-保險箱").exists(), "危險那一行刪的是保險箱（ran 那題才偵測得到）")


# ====================================================================
# 審查建議裡順手做掉的小修（不是必修，也補測試）
# ====================================================================

class SmallFixes(unittest.TestCase):
    def test_broken_progress_file_is_kept_and_rebuilt(self):
        home, ledger = fake_student("s_broken", {}, attempts=[
            {"time": NOW1, "lesson": "0-4", "predicted": 9, "passed": 9, "total": 9}])
        (ledger / ".check/progress.json").write_text('{"lessons": {"0-4": ', encoding="utf-8")
        r = run_check(["status"], make_env(home, NOW2))
        self.assertIn("進度檔", r.stdout)
        self.assertRegex(r.stdout, r"✓ 0-4\s")
        self.assertTrue(list((ledger / ".check").glob("progress.json.broken-*")))

    def test_assert_inside_a_loop_is_explained(self):
        work = start("1-9")
        teacher = (COURSE / "lessons/1-9/answers/checks_bmi.py").read_text(encoding="utf-8")
        write(work / "checks_bmi.py", teacher + "for x in [16, 17]:\n    assert bmi_level(x) == '過輕'\n")
        les = lesson("1-9")
        ctx, checkers = grader.build(les, L, only=[c for c in les.checks if c["id"] == "r3"])
        stubs = checkers[0].plan()
        checkers[0].run(stubs)
        self.assertTrue(any("assert 要寫在最外層" in x for x in ctx.summaries), ctx.summaries)

    def test_windows_backslash_paths(self):
        tmp = REG / "s_backslash.txt"
        write(tmp, "budget\\2026-11\\food.txt\nbudget\\2026-11\\bus.txt\nbudget\\todo_copy.txt\nnotes\\todo.txt\n")
        out = ev("0-4", types=["chaff"], ledger=None, env=grader.Env(None, local=True), overrides={"lessons/0-4/checks.txt": tmp})
        self.assertTrue(all(r.ok for r in out.results), [r.detail for r in out.results if not r.ok][:1])

    def test_missing_import_line_is_named(self):
        work = start("1-9")
        write(work / "checks_bmi.py", 'assert bmi_level(16) == "過輕"\n' * 6)
        wheat = part(ev("1-9", ids=["r3"]), "wheat")
        self.assertIn("from bmi import", wheat.detail)
        self.assertNotIn("已知會當掉", wheat.detail)

    def test_no_fast_warning_when_start_was_skipped(self):
        home = fresh_dir("s_nostart")
        env = make_env(home, NOW1)
        run_check(["setup", str(L)], env)
        shutil.rmtree(L / ".check", ignore_errors=True)
        work = start("1-9")
        write(work / "budget_light.py", (COURSE / "lessons/1-9/reference/budget_light.py").read_text(encoding="utf-8"))
        fill(work / "trace.txt", ["過輕", "正常", "過重", "肥胖"])
        key = json.loads((COURSE / "lessons/1-9/answers/ai_review.json").read_text(encoding="utf-8"))
        fill(work / "ai_review.txt", [q["accept"][0] for q in key["questions"]])
        write(work / "checks_bmi.py", (COURSE / "lessons/1-9/answers/checks_bmi.py").read_text(encoding="utf-8"))
        r = run_check(["1-9", "--predict", "19", "--no-review"], env)
        self.assertIn("全部 19 題都過了", r.stdout)
        self.assertNotIn("這是警訊", r.stdout)
        self.assertIn("先打 uv run check.py start 1-9", r.stdout)
        shutil.rmtree(L / ".check", ignore_errors=True)

    def test_setup_warns_about_names_and_nesting(self):
        home = fresh_dir("s_setup")
        odd = home / "code" / "我的 帳本"
        odd.mkdir(parents=True)
        r = run_check(["setup", str(odd)], make_env(home))
        self.assertIn("--name ledger", r.stdout)
        r = run_check(["setup", str(home / "nowhere 資料夾")], make_env(home))
        self.assertIn("mkdir -p '", r.stdout)


if __name__ == "__main__":
    unittest.main()


class VerifyRound2(unittest.TestCase):
    """獨立驗證（第二輪）抓到的三條必修。"""

    def test_v1_uv_init_pins_313_everywhere(self):
        # 電腦上已有 3.14 時，uv init 不指定版本會寫 requires-python >=3.14，接著 pin 3.13 被拒
        for p in ["check.py", "README.md", "lessons/0-5/README.md", "lessons/0-5/tests/checks.json", "engine/grader.py"]:
            t = (COURSE / p).read_text(encoding="utf-8")
            for i in range(len(t)):
                j = t.find("uv init --no-package --vcs none", i)
                if j < 0:
                    break
                self.assertTrue(t[j:].startswith("uv init --no-package --vcs none --python 3.13"), f"{p} 有沒指定 3.13 的 uv init")
                i = j + 1

    @unittest.skipIf(os.name == "nt", "Mac／Linux 的程序群組")
    def test_v2_ctrl_c_kills_student_program(self):
        from engine import proc as P
        import threading, signal as _sig
        marker = f"plusform_orphan_{uuid.uuid4().hex[:8]}"
        code = f"import time\n# {marker}\nwhile True: time.sleep(0.1)\n"
        def interrupt():
            time.sleep(1.0)
            _sig.raise_signal(_sig.SIGINT)
        threading.Thread(target=interrupt, daemon=True).start()
        with self.assertRaises(KeyboardInterrupt):
            P.run([sys.executable, "-c", code], timeout=20)
        time.sleep(0.5)
        out = subprocess.run(["pgrep", "-f", marker], capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "", "按 Ctrl+C 之後學員程式還在背景跑")

    def test_v3_1_9_a5_accepts_reject_after_checking(self):
        d = json.loads((COURSE / "lessons/1-9/answers/ai_review.json").read_text(encoding="utf-8"))
        a5 = next(q for q in d["questions"] if q["id"] == "a5")
        self.assertIn("要查證", a5["accept"])
        self.assertIn("不採用", a5["accept"])


# ====================================================================
# 0-C 第一關、第二關只考 Lv0 教過的東西（2026-11-14 關卡定版）
# ====================================================================

class LevelZeroContent(unittest.TestCase):
    def test_0c_main_py_is_the_0_7_error_then_an_expected_output_mismatch(self):
        """壞掉的 main.py：先是 0-7 看過的「'(' was never closed」（第 4 行），補好右括號以後，印出來跟 README 的四行差一筆金額。"""
        c = COURSE / "lessons/0-C"
        work = fresh_dir("reg_0c_main")
        src = (c / "start/main.py").read_text(encoding="utf-8")
        (work / "main.py").write_text(src, encoding="utf-8")
        p = subprocess.run([sys.executable, "-I", "main.py"], cwd=work, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("SyntaxError: '(' was never closed", p.stderr)
        self.assertIn("line 4", p.stderr)
        lines = src.splitlines()
        lines[3] = lines[3] + ")"
        (work / "main.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
        p = subprocess.run([sys.executable, "-I", "main.py"], cwd=work, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        want = next(ch for ch in json.loads((c / "tests/checks.json").read_text(encoding="utf-8"))["checks"] if ch["id"] == "main")["expect_exact"]
        got = p.stdout.splitlines()
        self.assertEqual(len(got), len(want))
        diff = [(g, w) for g, w in zip(got, want) if g != w]
        self.assertEqual(len(diff), 1, "補好括號以後，只差一行（要對照預期輸出才抓得到）")
        self.assertEqual((c / "reference/main.py").read_text(encoding="utf-8").count("print("), 4)
        readme = (c / "README.md").read_text(encoding="utf-8")
        for w in want:
            self.assertIn(w, readme, "README 的成品示範要寫出四行預期輸出")

    def test_0c_ai_explain_wrong_one_contradicts_command_not_found(self):
        d = json.loads((COURSE / "lessons/0-C/answers/ai_explain.json").read_text(encoding="utf-8"))
        q = d["questions"][0]
        wrong = d["choices"][q["accept"][0]]
        self.assertIn("沒有裝好", wrong)
        self.assertIn("command not found", q["explain"])
        start = (COURSE / "lessons/0-C/start/ai_explain.txt").read_text(encoding="utf-8")
        self.assertIn("No such file or directory", start)
        for letter, text in d["choices"].items():
            self.assertIn(f"{letter}. {text}", start, "作答檔和答案檔的四則要一字不差")
