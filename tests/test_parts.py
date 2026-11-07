"""零件測試：假的終端機、看得懂進度條、showcase、判分小工具、不連網、PEP 723。"""

from __future__ import annotations

import ast
import subprocess
import sys
import unittest

from _support import COURSE, fresh_dir, make_env

import concept_map  # noqa: E402
from engine import grader, vshell  # noqa: E402

HOME = "/Users/bear"
CWD = "/Users/bear/code/ledger"


class VShell(unittest.TestCase):
    def run_script(self, script, start=None):
        return vshell.run(script, HOME, CWD, start or ["notes/todo.txt"])

    def test_mkdir_p_and_without_p(self):
        r = self.run_script("mkdir -p a/b/c\nmkdir x/y")
        self.assertTrue(vshell.exists(r, CWD, "a/b/c/"))
        self.assertFalse(vshell.exists(r, CWD, "x/"))
        self.assertIn("No such file or directory", r.errors[0][1])

    def test_rm_rf_and_refuses_dotdot(self):
        r = self.run_script("rm -rf notes\nrm -rf ..")
        self.assertFalse(vshell.exists(r, CWD, "notes/todo.txt"))
        self.assertTrue(vshell.exists(r, CWD, "../"))
        self.assertIn('"." and ".." may not be removed', r.errors[0][1])

    def test_rm_dir_needs_r(self):
        r = self.run_script("rm notes")
        self.assertTrue(vshell.exists(r, CWD, "notes/"))
        self.assertTrue(r.errors)

    def test_cp_mv_cd_and_tilde(self):
        r = self.run_script("mkdir -p b\ncp notes/todo.txt b\nmv b/todo.txt b/done.txt\ncd ~\ntouch hi.txt")
        self.assertTrue(vshell.exists(r, CWD, "notes/todo.txt"))
        self.assertTrue(vshell.exists(r, CWD, "b/done.txt"))
        self.assertFalse(vshell.exists(r, CWD, "b/todo.txt"))
        self.assertTrue(vshell.exists(r, CWD, "~/hi.txt"))

    def test_and_chain_stops_after_error(self):
        r = self.run_script("cd nowhere && rm -rf notes")
        self.assertTrue(vshell.exists(r, CWD, "notes/"))

    def test_glob(self):
        r = self.run_script("touch notes/a.txt notes/b.md\nrm notes/*.txt")
        self.assertFalse(vshell.exists(r, CWD, "notes/a.txt"))
        self.assertTrue(vshell.exists(r, CWD, "notes/b.md"))


class ConceptMap(unittest.TestCase):
    def setUp(self):
        self.src = concept_map.SHOWCASE.read_text(encoding="utf-8")
        self.order = [x["id"] for x in grader.course_info(COURSE)["lessons"]]

    def test_showcase_size_and_every_line_tagged(self):
        lines = self.src.splitlines()
        self.assertTrue(150 <= len(lines) <= 250, len(lines))
        for info in concept_map.analyze_source(self.src):
            if info.text.strip():
                self.assertTrue(info.concepts, f"第 {info.lineno} 行沒有概念：{info.text}")
                self.assertNotIn("unknown", info.concepts, f"第 {info.lineno} 行用到課程沒教的寫法：{info.text}")

    def test_progress_from_zero_to_hundred(self):
        self.assertEqual(concept_map.progress(self.src, set()).percent, 0)
        self.assertEqual(concept_map.progress(self.src, set(self.order[: self.order.index("0-C") + 1])).percent, 0)
        self.assertEqual(concept_map.progress(self.src, set(self.order)).percent, 100)
        last = -1
        for i in range(len(self.order)):
            p = concept_map.progress(self.src, set(self.order[: i + 1])).percent
            self.assertGreaterEqual(p, last)
            last = p

    def test_specific_lines(self):
        by_text = {i.text.strip(): i.concepts for i in concept_map.analyze_source(self.src) if i.text.strip()}
        self.assertIn("call", by_text["amount = int(cleaned)"])
        self.assertIn("class", by_text["class Entry:"])
        self.assertIn("exception", by_text["except InvalidAmountError as error:"])
        self.assertIn("file", by_text['with open(path, "w", encoding="utf-8") as f:'])

    def test_name_aliases(self):
        self.assertEqual(concept_map.name_to_key("函式外殼"), "def")
        self.assertEqual(concept_map.name_to_key("if"), "if")
        self.assertEqual(concept_map.name_to_key("tuple 與 set"), "tuple_set")
        self.assertIsNone(concept_map.name_to_key("魔法"))


class Showcase(unittest.TestCase):
    def run_app(self, stdin, home=None):
        home = home or fresh_dir("showcase_home")
        env = make_env(home)  # 換掉 HOME，帳就存在假的家目錄
        r = subprocess.run([sys.executable, "-B", str(COURSE / "showcase" / "ledger_app.py")], input=stdin,
                           capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
        return r, home / ".pypy_ledger.txt"

    def test_normal_use(self):
        r, data = self.run_app("1\n2026-11-08\n午餐\n1\n120\n1\n\n公車\n2\nNT$1,500\n3\n4\n1000\n3\nq\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("第 1 個人付 334 元", r.stdout)
        self.assertIn("加總 1,000 元", r.stdout)
        rows = [line.split("\t") for line in data.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([int(x[3]) for x in rows], [120, 1500])
        r2, _ = self.run_app("2\nq\n", home=data.parent)  # 下次打開，帳還在
        self.assertIn("讀到 2 筆舊紀錄", r2.stdout)
        self.assertIn("合計 1,620 元", r2.stdout)

    def test_chinese_amount_crashes(self):
        r, _data = self.run_app("1\n2026-11-08\n早餐\n1\n一百元\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ValueError", r.stderr)
        self.assertIn("一百", r.stderr)


class GraderBits(unittest.TestCase):
    def test_norm_answer(self):
        self.assertEqual(grader.norm_answer("~/code/", "path", HOME), "/Users/bear/code")
        self.assertEqual(grader.norm_answer(" 允 許 ", "text"), "允許")
        self.assertEqual(grader.norm_answer("ｂ", "text"), "b")

    def test_normalize_id(self):
        info = grader.course_info(COURSE)
        self.assertEqual(grader.normalize_id("1-09", info), "1-9")
        self.assertEqual(grader.normalize_id("LV0", info), "0-C")
        self.assertEqual(grader.normalize_id("0-c", info), "0-C")
        self.assertEqual(grader.normalize_id("env", info), "0-5")

    def test_system_python_detection(self):
        self.assertTrue(grader.is_system_python("/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9"))
        self.assertTrue(grader.is_system_python("/usr"))
        self.assertFalse(grader.is_system_python("/Users/bear/.local/share/uv/python/cpython-3.13.13-macos-aarch64-none"))
        self.assertFalse(grader.is_system_python("C:/Users/bear/AppData/Roaming/uv/python/cpython-3.13"))


NETWORK_MODULES = {"socket", "ssl", "urllib", "http", "requests", "httpx", "ftplib", "smtplib", "aiohttp", "anthropic", "openai"}


class NoNetworkStdlibOnly(unittest.TestCase):
    FILES = ["check.py", "concept_map.py", "engine/grader.py", "engine/runner.py", "engine/state.py", "engine/vshell.py",
             "engine/proc.py", "tools/validate_lesson.py", "tests/run_all.py"]

    def test_no_network_imports_and_stdlib_only(self):
        local = {"engine", "concept_map", "_support"}
        for rel in self.FILES:
            tree = ast.parse((COURSE / rel).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module.split(".")[0]]
                for name in names:
                    self.assertNotIn(name, NETWORK_MODULES, f"{rel} import 了 {name}")
                    if name not in local:
                        self.assertIn(name, sys.stdlib_module_names, f"{rel} 用了標準庫以外的 {name}")

    def test_pep723_header(self):
        for rel in ("check.py", "concept_map.py", "tools/validate_lesson.py", "tests/run_all.py"):
            head = (COURSE / rel).read_text(encoding="utf-8").splitlines()[:4]
            self.assertEqual(head[0], "# /// script")
            self.assertIn('# requires-python = ">=3.13"', head)


if __name__ == "__main__":
    unittest.main()
