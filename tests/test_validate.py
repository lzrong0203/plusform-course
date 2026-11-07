"""老師端工具 tools/validate_lesson.py：真的課程要全過；故意改壞的題目要被擋下來。"""

from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, make_env, fresh_dir, snapshot


def validate(args, root=None):
    home = fresh_dir("validate_home")
    cmd = [sys.executable, "-B", str(COURSE / "tools" / "validate_lesson.py"), *args]
    if root:
        cmd += ["--root", str(root)]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=make_env(home), timeout=600)


def copy_course(name):
    dest = WS / name
    if dest.exists():
        shutil.rmtree(dest)
    def ignore(folder, names):
        skip = {".git", "__pycache__"}
        if Path(folder) == COURSE:
            skip.add("tests")  # 只略過最外層的 tests/，每課自己的 tests/ 要留著
        return [n for n in names if n in skip]

    shutil.copytree(COURSE, dest, ignore=ignore)
    return dest


class Validate(unittest.TestCase):
    @unittest.skipIf(UV is None, "需要 uv（0-5 要建臨時帳本）")
    def test_real_course_is_valid(self):
        before = snapshot(COURSE)
        r = validate([])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("全部沒問題", r.stdout)
        self.assertIn("壞版本 bmi_m1.py 會讓 老師的標準檢查 變紅", r.stdout)
        self.assertIn("壞版本 doctor_m1.py 會讓 老師的標準檢查 變紅", r.stdout)
        self.assertIn("例外：「函式定義」（1-18 才教）", r.stdout)
        self.assertEqual(snapshot(COURSE), before)

    def test_mutant_that_is_not_broken(self):
        root = copy_course("validate_copy_same")
        ref = (root / "lessons/1-9/reference/bmi.py").read_text(encoding="utf-8")
        (root / "lessons/1-9/mutants/bmi_m2.py").write_text(ref.replace("正確版", "壞版本 2") + "\n# 多一行註解\n", encoding="utf-8")
        r = validate(["1-9"], root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("壞版本 bmi_m2.py 跟正確版一模一樣", r.stdout)
        self.assertIn("壞版本 bmi_m2.py 沒有讓任何參考測試變紅", r.stdout)

    def test_mutant_using_unlearned_concept(self):
        root = copy_course("validate_copy_concept")
        path = root / "lessons/1-9/mutants/bmi_m1.py"
        path.write_text(path.read_text(encoding="utf-8") + "\n\nLEVELS = {'過輕': 0}\nfor name in LEVELS:\n    pass\n", encoding="utf-8")
        r = validate(["1-9"], root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("mutants/bmi_m1.py 用到 CONCEPTS.md 沒列的概念", r.stdout)
        self.assertIn("dict", r.stdout)

    def test_shell_mutant_with_unlisted_command_and_wrong_reference(self):
        root = copy_course("validate_copy_shell")
        (root / "lessons/0-4/mutants/agent_m2.sh").write_text("sudo mkdir -p budget/2026-11\n", encoding="utf-8")
        (root / "lessons/0-4/answers/checks.txt").write_text("budget/2026-11/food.txt\nbudget/wrong.txt\n", encoding="utf-8")
        r = validate(["0-4"], root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("用到 CONCEPTS.md 沒列的指令：sudo", r.stdout)
        self.assertIn("正確版沒通過老師的標準檢查", r.stdout)

    def test_readme_sections_and_answer_count(self):
        root = copy_course("validate_copy_readme")
        readme = root / "lessons/0-C/README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace("## 6. 怎麼交", "## 6. 其他"), encoding="utf-8")
        pwd = root / "lessons/0-C/start/pwd.txt"
        pwd.write_text(pwd.read_text(encoding="utf-8") + "\n第 6 題：cd ..\n答：\n", encoding="utf-8")
        r = validate(["0-C"], root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("README 少了這幾段：怎麼交", r.stdout)
        self.assertIn("pwd.txt 有 6 個「答：」", r.stdout)


if __name__ == "__main__":
    unittest.main()
