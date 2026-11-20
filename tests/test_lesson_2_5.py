"""2-5〈SQLite 與 SQL 基礎〉：作業與 check 的回歸測試（每課自己一個測試檔，不改 test_regressions.py）。

沒有新加 grader 欄位：用前幾課就有的 run 的 sandbox（copy、probe、steps；probe 放課程的 entries.csv、ledger_db.py 和 check 用的小程式）、
answers、filled、pytest_chaff（extra_files 放 entries.csv、ledger_db.py）、git_commits（saved_before）。
pytest 用 uv add --dev --offline 從 uv 的快取裝（不連網；沒有快取時這幾條測試會失敗，先在任何地方 uv add --dev pytest 一次）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv 和 git。
"""

from __future__ import annotations

import shutil
import sqlite3
import subprocess
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, git, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l205"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "2-5"
D = COURSE / "lessons" / LID


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


def ref(name: str) -> None:
    shutil.copyfile(D / "reference" / name, mine(name))


def ev(ids: list[str], ledger: Path | None = L) -> grader.Outcome:
    les = grader.load_lesson(LID, COURSE)
    return grader.evaluate(les, ledger, only=[c for c in les.checks if c["id"] in ids])


def by(out: grader.Outcome) -> dict[str, grader.Result]:
    return {r.id: r for r in out.results}


def uv(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([UV, *args], cwd=L, env=grader.child_env(), capture_output=True, text=True)


def run_py(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([UV, "run", "--offline", "--quiet", *args], cwd=L, env=grader.child_env(), capture_output=True, text=True)


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


def setUpModule():
    if UV is None or shutil.which("git") is None:
        raise unittest.SkipTest("需要 uv 和 git")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)
    r = uv("add", "--dev", "pytest", "--offline", "--quiet")
    if r.returncode != 0:
        raise AssertionError("uv add pytest --offline 失敗（uv 的快取裡沒有 pytest？）：" + r.stderr[-400:])


class Basics(unittest.TestCase):
    def test_lesson_id_forms(self):
        course = grader.course_info(COURSE)
        for raw in ("2-5", "2-05", "２－５"):
            self.assertEqual(grader.normalize_id(raw, course), "2-5")
        self.assertIn("2-5", grader.available_lessons(COURSE))

    def test_csv_version_totals(self):
        """開場的 CSV 版：11 月四類的合計（影片、需求卡、test_totals 都用這四個數字）。"""
        start()
        p = run_py("lessons/2-5/csv_totals.py")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.split("\n")[:4], ["餐飲 635", "交通 500", "日用品 680", "娛樂 320"])

    def test_start_import_breaks_on_quote(self):
        """起點的 import_csv.py：補上 CREATE TABLE 以後，f-string 拼的 INSERT 在「熊's 生日蛋糕」那一筆壞掉。"""
        start()
        text = mine("import_csv.py").read_text(encoding="utf-8").replace(
            "# 換你寫：建一個資料表 entries（五欄：date、item、category、amount、note）",
            'con.execute("CREATE TABLE entries (date TEXT, item TEXT, category TEXT, amount INTEGER, note TEXT)")')
        write(mine("import_csv.py"), text)
        p = run_py("lessons/2-5/import_csv.py")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('sqlite3.OperationalError: near "s": syntax error', p.stderr)
        self.assertIn("'熊's 生日蛋糕')", p.stdout.split("\n")[-2])
        self.assertEqual(len([x for x in p.stdout.split("\n") if x.startswith("INSERT")]), 9)

    def test_run_sql_tool(self):
        """run_sql.py：q2.sql（正確版）跑 practice.db；tiny.sql 有 CREATE TABLE，跑在記憶體資料庫（不動 practice.db）。"""
        start()
        ref("import_csv.py")
        self.assertIn("一共 11 筆", run_py("lessons/2-5/import_csv.py").stdout)
        ref("q2.sql")
        p = run_py("lessons/2-5/run_sql.py", "q2.sql")
        self.assertEqual(p.stdout.split("\n")[:5], ["category | SUM(amount)", "交通 | 500", "娛樂 | 320", "日用品 | 680", "餐飲 | 635"])
        ref("tiny.sql")
        p = run_py("lessons/2-5/run_sql.py", "tiny.sql")
        self.assertEqual(p.stdout.split("\n")[:3], ["category | COUNT(*) | COUNT(amount) | AVG(amount)", "交通 | 3 | 2 | 45.0", "餐飲 | 2 | 2 | 150.0"])
        con = sqlite3.connect(mine("practice.db"))
        self.assertEqual(con.execute("SELECT name FROM sqlite_master").fetchall(), [("entries",)])
        con.close()

    def test_entries_fake(self):
        raw = (D / "start" / "entries.csv").read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        import re
        self.assertIsNone(re.search(rb"\d{8,}", raw))


class Ring1(unittest.TestCase):
    IDS = ["import", "q1", "q2"]

    def setUp(self):
        start()

    def test_start_all_fail(self):
        rs = by(ev(self.IDS))
        for k, r in rs.items():
            self.assertFalse(r.ok, k)
        self.assertIn("CREATE TABLE", rs["import"].detail)

    def test_reference_all_pass(self):
        for name in ("import_csv.py", "q1.sql", "q2.sql"):
            ref(name)
        rs = by(ev(self.IDS))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_fstring_with_create_fails(self):
        """建了表、INSERT 還是 f-string：第 1 步就當掉，提示講問號。"""
        text = mine("import_csv.py").read_text(encoding="utf-8").replace(
            "# 換你寫：建一個資料表 entries（五欄：date、item、category、amount、note）",
            'con.execute("CREATE TABLE entries (date TEXT, item TEXT, category TEXT, amount INTEGER, note TEXT)")')
        write(mine("import_csv.py"), text)
        r = by(ev(["import"]))["import"]
        self.assertFalse(r.ok)
        self.assertIn("?, ?, ?, ?, ?", r.detail)

    def test_q2_without_not_null_fails(self):
        """影片裡第一次寫的 q2（沒有 amount IS NOT NULL）：多一列 醫療 | None。"""
        write(mine("q2.sql"), "SELECT category, SUM(amount) FROM entries\nWHERE date LIKE '2026-11%'\nGROUP BY category;\n")
        r = by(ev(["q2"]))["q2"]
        self.assertFalse(r.ok)
        self.assertIn("醫療 | None", r.detail)

    def test_q2_alias_and_order_ok(self):
        """欄位取別名、加 ORDER BY 也算對（列排序後比）。"""
        write(mine("q2.sql"), "select category as 分類, sum(amount) as 合計\nfrom entries\nwhere date like '2026-11%' and amount is not null\ngroup by category\norder by 合計 desc;\n")
        r = by(ev(["q2"]))["q2"]
        self.assertTrue(r.ok, r.detail)

    def test_q1_select_star_fails(self):
        write(mine("q1.sql"), "SELECT * FROM entries WHERE category = '餐飲';\n")
        self.assertFalse(by(ev(["q1"]))["q1"].ok)

    def test_sql_answers(self):
        answer("sql.txt", ["A", "C", "B"])
        rs = by(ev(["sql"]))
        self.assertTrue(all(r.ok for r in rs.values()), [(r.id, r.detail) for r in rs.values()])

    def test_ledger_untouched(self):
        for name in ("import_csv.py", "q1.sql", "q2.sql"):
            ref(name)
        before = snapshot(L)
        ev(self.IDS)
        self.assertEqual(snapshot(L), before)


class Ring2(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_tiny_fails(self):
        r = by(ev(["tiny"]))["tiny"]
        self.assertFalse(r.ok)

    def test_tiny_five_without_null_fails(self):
        write(mine("tiny.sql"), (D / "reference" / "tiny.sql").read_text(encoding="utf-8").replace("('交通', NULL)", "('交通', 10)"))
        self.assertFalse(by(ev(["tiny"]))["tiny"].ok)

    def test_reference_and_forms(self):
        ref("tiny.sql")
        answer("null.txt", ["B", "A", "C"])
        fill("verify.md", {"我問 AI 的 SQL：": "COUNT 和 AVG 那一條", "AI 的解釋：": "AVG 是平均", "我的 5 筆小資料：": "交通 50、NULL、40",
                           "跑出來的結果：": "交通 3 2 45.0", "AI 說的對不對、哪裡不一樣：": "對，AVG 跳過 NULL"})
        rs = by(ev(["tiny", "null", "verify"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))


class Ring3(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_test_only_count(self):
        """起點只有 test_count：正確版過、三個壞版本都溜過去（它們筆數一樣）。"""
        rs = by(ev(["accept"]))
        self.assertTrue(rs["accept-wheat"].ok, rs["accept-wheat"].detail)
        for m in ("m1", "m2", "m3"):
            self.assertFalse(rs[f"accept-{m}"].ok, m)

    def test_totals_catches_all(self):
        """影片裡熊打的 test_totals（CSV 版的四個數字）抓得到三個壞版本。"""
        write(mine("tests/test_db.py"), (D / "answers" / "test_db.py").read_text(encoding="utf-8"))
        rs = by(ev(["accept"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_wrong_expectation(self):
        """手算時把退票也加進去（交通 920）：正確版就沒過。"""
        write(mine("tests/test_db.py"), (D / "answers" / "test_db.py").read_text(encoding="utf-8").replace('"交通": 500', '"交通": 920'))
        self.assertFalse(by(ev(["accept"]))["accept-wheat"].ok)

    def test_hidden(self):
        """隱藏帳：課程凍結的 AI 版本（amount > 0）沒過；熊在影片裡改的那一行（IS NOT NULL）過；沒有 db_report.py 時提示 cp。"""
        r = by(ev(["hidden"]))["hidden"]
        self.assertFalse(r.ok)
        self.assertIn("cp lessons/2-5/ai_db_report.py", r.detail)
        shutil.copyfile(mine("ai_db_report.py"), mine("db_report.py"))
        self.assertFalse(by(ev(["hidden"]))["hidden"].ok)
        write(mine("db_report.py"), mine("ai_db_report.py").read_text(encoding="utf-8").replace("amount > 0", "amount IS NOT NULL"))
        r = by(ev(["hidden"]))["hidden"]
        self.assertTrue(r.ok, r.detail)

    def test_saved_and_decision(self):
        if (L / ".git").exists():
            shutil.rmtree(L / ".git")
        git(L, "init", "-q")
        git(L, "add", "-A")
        git(L, "commit", "-q", "-m", "交辦前")
        ref("db_report.py")
        write(mine("tests/test_db.py"), (D / "answers" / "test_db.py").read_text(encoding="utf-8"))
        git(L, "add", "-A")
        git(L, "commit", "-q", "-m", "月合計查詢")
        fill("decision.md", {"它跑了什麼指令：": "uv run pytest lessons/2-5", "uv run pytest 的結果：": "1 failed", "哪一類的合計不對、為什麼：": "交通，amount > 0 跳過退票",
                             "我改了哪一行：": "WHERE 那一行", "收不收，為什麼：": "改好才收"})
        rs = by(ev(["saved", "decision"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))


if __name__ == "__main__":
    unittest.main()
