"""2-2〈套件與虛擬環境：uv add、pyproject、uv.lock〉：作業與 check 的回歸測試（每課自己一個測試檔，不改 test_regressions.py）。

grader 加的兩種（只對寫了它的題目生效）：
  uv_deps    pyproject.toml 的 dependencies 和 uv.lock 都有這個套件（用 uv add 裝的）
  uv_locked  乾淨複本：pyproject.toml、uv.lock、.python-version、report.py 複製到暫存資料夾，uv sync --locked --offline 建新的 .venv 再跑，
             表格每一列對齊（中文字算兩格）；pip／uv pip install 裝進帳本 .venv、沒寫進 pyproject.toml 的套件在這裡會找不到
不依賴網路和 uv 的快取（2026-11-19 改：快取會被暫存清理或別課清掉，原本的 uv add rich --offline 找不到 markdown-it-py 就整批壞）：
  uv_deps、git_commits 只讀 pyproject.toml、uv.lock、存檔點，用 fake_add_rich 照 uv add rich 寫進去的樣子改這兩個檔；
  乾淨複本大多用沒有第三方套件的帳本（uv sync --locked --offline 不用快取），「手改 pyproject.toml」用 requires-python 那一行（離線也看得出 uv.lock 對不上）；
  只有真的要跑 rich 的幾條（CleanRich、Whole）用 real_add_rich：uv 的快取裡沒有 rich 和它要的套件就跳過，印出原因（要跑：在任何 uv 專案連網打一次 uv add rich）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv 和 git。
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, git, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l202"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "2-2"
D = COURSE / "lessons" / LID
RIGHT = ["C", "A", "B"]
ROWS = next(c for c in json.loads((D / "tests" / "checks.json").read_text(encoding="utf-8"))["checks"] if c["id"] == "clean")["rows"]

# 三種「表格」：rich 的（對齊）、prettytable 的（對齊，可是套件沒寫進 pyproject.toml）、只照字數補空格的（日用品歪掉）
PRETTY = '''from prettytable import PrettyTable

table = PrettyTable(["分類", "金額"])
table.align["分類"] = "l"
table.align["金額"] = "r"
for category, amount in totals.items():
    table.add_row([category, f"{amount:,} 元"])
table.add_row(["合計", f"{sum(totals.values()):,} 元"])
print(table)
'''
LJUST = '''print("11 月月報")
for category, amount in totals.items():
    print(f"| {category:<4} | {amount:>5,} 元 |")
print(f"| {'合計':<4} | {sum(totals.values()):>5,} 元 |")
'''


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


def head_of_start() -> str:
    """起點 report.py 算好 totals 的那一段（print 之前）。"""
    text = (D / "start" / "report.py").read_text(encoding="utf-8")
    return text[: text.index('print("11 月月報")')]


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


def uv(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([UV, *args], cwd=L, env=grader.child_env(), capture_output=True, text=True)


def pyproject_deps(deps: list[str]) -> None:
    p = L / "pyproject.toml"
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"dependencies = \[[^\]]*\]", "dependencies = [" + ", ".join(json.dumps(d) for d in deps) + "]", text)
    p.write_text(text, encoding="utf-8")


_BASELINE: dict[str, bytes] = {}   # 剛 uv init 的 pyproject.toml、uv.lock（setUpModule 存）
_RICH_SKIP: list[str] = []


def reset_deps() -> None:
    """pyproject.toml、uv.lock 回到剛 uv init 的樣子（沒有第三方套件）。不用 uv remove：重新鎖定要網路或快取。"""
    for name, data in _BASELINE.items():
        (L / name).write_bytes(data)


def fake_add_rich() -> None:
    """照 uv add rich（uv 0.13.8，2026-11-19 實跑）寫進 pyproject.toml、uv.lock 的樣子改這兩個檔，不裝套件、不連網、不用快取。
    uv_deps 只讀這兩個檔、git_commits 只看存檔點，用這個就夠；乾淨複本要真的跑 rich 的用 real_add_rich。"""
    reset_deps()
    pyproject_deps(["rich>=15.0.0"])
    lock = L / "uv.lock"
    text = lock.read_text(encoding="utf-8").rstrip()
    assert text.endswith('source = { virtual = "." }'), text[-200:]   # 剛 uv init：帳本自己那一段在最後
    text += ('\ndependencies = [\n    { name = "rich" },\n]\n\n[package.metadata]\nrequires-dist = [{ name = "rich", specifier = ">=15.0.0" }]\n\n'
             '[[package]]\nname = "rich"\nversion = "15.0.0"\nsource = { registry = "https://pypi.org/simple" }\n')
    lock.write_text(text, encoding="utf-8")


def real_add_rich() -> None:
    """真的 uv add rich（--offline：只用 uv 的快取，不連網）。快取裡沒有 rich 和它要的套件（markdown-it-py、mdurl、pygments）就跳過，印出原因。"""
    if _RICH_SKIP:
        raise unittest.SkipTest(_RICH_SKIP[0])
    reset_deps()
    r = uv("add", "rich", "--offline", "--quiet")
    if r.returncode != 0:
        reset_deps()
        lines = [ln.strip(" ×╰─▶") for ln in r.stderr.splitlines() if ln.strip()]
        last = next((ln for ln in lines if "Failed to" in ln or "not found" in ln), lines[0] if lines else "")   # 例：Failed to download `markdown-it-py==4.3.0`
        _RICH_SKIP.append("uv 的快取裡沒有 rich 和它要的套件，要真的裝 rich 的測試跳過（測試不連網）。"
                          "要跑這幾條：在任何 uv 專案連網打一次 uv add rich。uv 的訊息：" + last[-200:])
        print("\n[test_lesson_2_2] SKIP " + _RICH_SKIP[0], file=sys.stderr)
        raise unittest.SkipTest(_RICH_SKIP[0])


def save(msg: str) -> None:
    git(L, "add", "-A")
    git(L, "commit", "-q", "--allow-empty", "-m", msg)


def fresh_repo() -> None:
    if (L / ".git").exists():
        shutil.rmtree(L / ".git")
    git(L, "init", "-q")


def setUpModule():
    if UV is None or shutil.which("git") is None:
        raise unittest.SkipTest("需要 uv 和 git")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)
    for name in ("pyproject.toml", "uv.lock"):
        _BASELINE[name] = (L / name).read_bytes()


class Basics(unittest.TestCase):
    def test_lesson_id_forms(self):
        course = grader.course_info(COURSE)
        for raw in ("2-2", "2-02", "２－２"):
            self.assertEqual(grader.normalize_id(raw, course), "2-2")
        self.assertIn("2-2", grader.available_lessons(COURSE))

    def test_start_report_is_crooked(self):
        """起點的 report.py 照字數補空格：日用品那一行的金額往右多兩格（中文字在終端機佔兩格）。"""
        p = subprocess.run(["python3", "-I", "-B", str(D / "start" / "report.py")], capture_output=True, text=True, check=True)
        lines = p.stdout.splitlines()
        self.assertEqual(lines[3], "日用品    448 元")
        probs = grader.table_problems(p.stdout, ROWS)
        self.assertEqual(len(probs), 1, probs)
        self.assertIn("「日用品」那一行的金額沒對齊", probs[0])
        self.assertIn("右邊 2 格", probs[0])

    def test_rows_add_up(self):
        """rows 的金額就是起點資料的加總（合計 2,593）。"""
        ns: dict = {}
        exec(compile(head_of_start(), "report.py", "exec"), ns)
        want = [[k, f"{v:,}"] for k, v in ns["totals"].items()] + [["合計", f"{sum(ns['totals'].values()):,}"]]
        self.assertEqual(want, ROWS)

    def test_key_letters_spread(self):
        key = json.loads((D / "answers" / "deps.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"] for q in key["questions"]], [[x] for x in RIGHT])


class TableShape(unittest.TestCase):
    """table_problems：只看每一列的分類開頭、金額最後一個數字對不對齊（中文字兩格），框線、標題怎麼畫都可以。"""

    RICH = ("      11 月月報      \n┏━━━━━━━━┳━━━━━━━━━━┓\n┃ 分類   ┃     金額 ┃\n┡━━━━━━━━╇━━━━━━━━━━┩\n│ 餐飲   │ 1,250 元 │\n│ 交通   │   320 元 │\n"
            "│ 日用品 │   448 元 │\n│ 娛樂   │   480 元 │\n│ 其他   │    95 元 │\n│ 合計   │ 2,593 元 │\n└────────┴──────────┘\n")

    def test_rich_table_ok(self):
        self.assertEqual(grader.table_problems(self.RICH, ROWS), [])

    def test_plain_aligned_ok(self):
        text = "11 月月報\n餐飲    1,250 元\n交通      320 元\n日用品    448 元\n娛樂      480 元\n其他       95 元\n合計    2,593 元\n"
        self.assertEqual(grader.table_problems(text, ROWS), [])

    def test_ljust_counts_characters_not_columns(self):
        """f"{category:<4}" 照字數補：日用品比別人寬兩格。"""
        ns: dict = {}
        out = []
        ns["print"] = lambda *a: out.append(" ".join(str(x) for x in a))
        exec(compile(head_of_start() + LJUST, "report.py", "exec"), ns)
        probs = grader.table_problems("\n".join(out), ROWS)
        self.assertTrue(probs)
        self.assertIn("日用品", probs[0])

    def test_missing_total(self):
        text = self.RICH.replace("合計", "總計")
        probs = grader.table_problems(text, ROWS)
        self.assertIn("找不到「合計」", probs[0])

    def test_amount_without_comma_not_found(self):
        text = self.RICH.replace("1,250", " 1250")
        self.assertIn("找不到「餐飲」和 1,250", grader.table_problems(text, ROWS)[0])

    def test_left_aligned_amounts(self):
        text = self.RICH.replace("│   320 元 │", "│ 320 元   │")
        probs = grader.table_problems(text, ROWS)
        self.assertIn("「交通」那一行的金額沒對齊", probs[0])
        self.assertIn("左邊 2 格", probs[0])


class Deps(unittest.TestCase):
    def setUp(self):
        start()
        reset_deps()

    def test_not_added(self):
        r = ev(["rich"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("uv add rich", r.detail)

    def test_uv_add_passes(self):
        fake_add_rich()
        r = ev(["rich"]).results[0]
        self.assertTrue(r.ok, r.detail)
        self.assertIn("rich", r.note)

    def test_hand_edited_pyproject_not_locked(self):
        """手改 pyproject.toml 加 rich、沒有 uv lock：uv.lock 裡沒有它。"""
        pyproject_deps(["rich>=15.0.0"])
        r = ev(["rich"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("uv.lock 卻沒有", r.detail)
        pyproject_deps([])

    def test_lookalike_name_not_rich(self):
        """rich-toolkit、markdown-it-py 不是 rich。"""
        pyproject_deps(["rich-toolkit>=0.1", "markdown-it-py>=4.0"])
        self.assertFalse(ev(["rich"]).results[0].ok)
        pyproject_deps([])

    def test_name_normalized(self):
        self.assertEqual(grader._dep_names(["Rich>=15", "markdown_it.py ; python_version>'3'", 3]), {"rich", "markdown-it-py"})


class Clean(unittest.TestCase):
    """乾淨複本：不碰帳本，在暫存資料夾裡 uv sync --locked 再跑。這一組的帳本沒有第三方套件（離線、不用 uv 的快取）。"""

    def setUp(self):
        start()
        reset_deps()

    def test_start_runs_but_crooked(self):
        r = ev(["clean"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("表格還沒對齊", r.detail)
        self.assertIn("日用品", r.detail)

    def test_ledger_untouched(self):
        before = snapshot(L)
        ev(["clean"])
        self.assertEqual(snapshot(L), before)

    def test_package_not_in_pyproject(self):
        """uv pip install prettytable 裝進帳本 .venv、pyproject.toml 沒變：乾淨複本上找不到 prettytable。"""
        write(mine("report.py"), head_of_start() + PRETTY)
        r = ev(["clean"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("找不到 prettytable 這個套件", r.detail)
        self.assertIn("uv add prettytable", r.detail)

    def test_rich_not_in_pyproject(self):
        """report.py 用 rich，可是 pyproject.toml（和 uv.lock）沒有 rich：乾淨複本上 import rich 失敗。"""
        write(mine("report.py"), ref("report.py"))
        r = ev(["clean"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("找不到 rich 這個套件", r.detail)

    def test_lock_out_of_date(self):
        """手改 pyproject.toml、沒有 uv lock：--locked 停下來，不偷偷更新 uv.lock（改 requires-python，離線也看得出對不上）。"""
        p = L / "pyproject.toml"
        p.write_text(p.read_text(encoding="utf-8").replace('requires-python = ">=3.13"', 'requires-python = ">=3.12"'), encoding="utf-8")
        r = ev(["clean"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("uv.lock 跟 pyproject.toml 對不上", r.detail)

    def test_no_lock(self):
        (L / "uv.lock").unlink()
        r = ev(["clean"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("找不到 uv.lock", r.detail)

    def test_crash_shows_tail(self):
        write(mine("report.py"), (D / "start" / "report.py").read_text(encoding="utf-8") + "print(1 / 0)\n")
        r = ev(["clean"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("ZeroDivisionError", r.detail)


class CleanRich(unittest.TestCase):
    """真的 uv add rich 以後的乾淨複本（要 uv 的快取裡有 rich；沒有就整組跳過，見 real_add_rich）。"""

    @classmethod
    def setUpClass(cls):
        start()
        real_add_rich()

    @classmethod
    def tearDownClass(cls):
        reset_deps()

    def setUp(self):
        start()

    def test_real_uv_add_passes_deps(self):
        r = ev(["rich"]).results[0]
        self.assertTrue(r.ok, r.detail)

    def test_reference_passes(self):
        write(mine("report.py"), ref("report.py"))
        r = ev(["clean"]).results[0]
        self.assertTrue(r.ok, r.detail)

    def test_reference_ledger_untouched(self):
        write(mine("report.py"), ref("report.py"))
        before = snapshot(L)
        ev(["clean"])
        self.assertEqual(snapshot(L), before)

    def test_added_package_not_locked(self):
        """手改 pyproject.toml 多寫一個套件、沒有 uv lock：--locked 停下來（pygments 是 rich 要的，快取裡一定有）。"""
        write(mine("report.py"), ref("report.py"))
        p = L / "pyproject.toml"
        old = p.read_text(encoding="utf-8")
        p.write_text(old.replace('"rich>=', '"pygments>=2.0",\n    "rich>='), encoding="utf-8")
        try:
            r = ev(["clean"]).results[0]
            self.assertFalse(r.ok)
            self.assertIn("uv.lock 跟 pyproject.toml 對不上", r.detail)
        finally:
            p.write_text(old, encoding="utf-8")


class Answers(unittest.TestCase):
    def setUp(self):
        start()

    def test_right_answers(self):
        answer("deps.txt", RIGHT)
        out = ev(["deps"])
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        self.assertEqual(len(out.results), 3)

    def test_venv_in_git_is_wrong(self):
        """以為 .venv 也在存檔點裡（第 2 題選 C）、以為 uv pip install 也算（第 3 題選 A）。"""
        answer("deps.txt", ["C", "C", "A"])
        out = ev(["deps"])
        self.assertEqual([r.ok for r in out.results], [True, False, False])


class Saved(unittest.TestCase):
    """交辦前先存檔；收下後 pyproject.toml、uv.lock、report.py 都要存進存檔點。"""

    @classmethod
    def setUpClass(cls):
        start()
        fake_add_rich()

    @classmethod
    def tearDownClass(cls):
        reset_deps()

    def setUp(self):
        start()
        fresh_repo()

    def test_saved_then_kept_and_saved(self):
        save("交辦前")
        write(mine("report.py"), ref("report.py"))
        save("報表表格")
        r = ev(["saved"]).results[0]
        self.assertTrue(r.ok, r.detail)

    def test_lock_changed_not_saved(self):
        """收下後 uv.lock 又變了（例如 agent 多裝了套件）卻沒存：uv.lock 還沒按存檔點。"""
        save("交辦前")
        write(mine("report.py"), ref("report.py"))
        save("報表表格")
        lock = L / "uv.lock"
        keep = lock.read_bytes()
        lock.write_bytes(keep + b"\n")
        try:
            r = ev(["saved"]).results[0]
            self.assertFalse(r.ok)
            self.assertIn("uv.lock 改過之後還沒按存檔點", r.detail)
        finally:
            lock.write_bytes(keep)

    def test_never_saved_original(self):
        write(mine("report.py"), ref("report.py"))
        save("報表表格")
        save("再一個")
        r = ev(["saved"]).results[0]
        self.assertFalse(r.ok)
        self.assertIn("原本的樣子", r.detail)


class Forms(unittest.TestCase):
    def setUp(self):
        start()

    def test_empty_forms_fail(self):
        self.assertFalse(ev(["pypi"]).results[0].ok)
        self.assertFalse(ev(["decision"]).results[0].ok)

    def test_filled_forms_pass(self):
        fill("pypi.md", {"套件名稱，我對過拼法了：": "rich", "維護者（maintainer）：": "willmcgugan",
                         "最近一次發布（Key dates 的 Released）：": "2026 年 4 月", "原始碼在哪裡（Project links 的連結）：": "GitHub 上的 Textualize/rich"})
        fill("decision.md", {"它要執行的指令：": "uv run lessons/2-2/report.py", "它有沒有裝套件、怎麼裝的：": "沒有裝，用已經裝好的 rich",
                             "pyproject.toml 和 uv.lock 有沒有變：": "沒有變", "check 的結果（乾淨複本）：": "全過", "收不收，為什麼：": "收，乾淨複本跑得起來"})
        self.assertTrue(ev(["pypi"]).results[0].ok, ev(["pypi"]).results[0].detail)
        self.assertTrue(ev(["decision"]).results[0].ok)


class Whole(unittest.TestCase):
    def test_all_right(self):
        start()
        real_add_rich()
        self.addCleanup(reset_deps)
        fresh_repo()
        answer("deps.txt", RIGHT)
        fill("pypi.md", {"套件名稱，我對過拼法了：": "rich", "維護者（maintainer）：": "willmcgugan",
                         "最近一次發布（Key dates 的 Released）：": "2026-04-12", "原始碼在哪裡（Project links 的連結）：": "github.com/Textualize/rich"})
        fill("decision.md", {"它要執行的指令：": "uv run", "它有沒有裝套件、怎麼裝的：": "沒有", "pyproject.toml 和 uv.lock 有沒有變：": "沒變",
                             "check 的結果（乾淨複本）：": "全過", "收不收，為什麼：": "收下"})
        save("交辦前")
        write(mine("report.py"), ref("report.py"))
        save("報表表格")
        les = grader.load_lesson(LID, COURSE)
        out = grader.evaluate(les, L)
        bad = [(r.id, r.detail) for r in out.results if not r.ok]
        self.assertEqual(bad, [])
        self.assertEqual(len(out.results), 2 + 3 + 3)   # 第一圈 2、第二圈 3、第三圈 3


if __name__ == "__main__":
    unittest.main()
