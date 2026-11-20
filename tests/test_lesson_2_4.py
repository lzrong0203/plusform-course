"""2-4〈CSV 與 JSON：匯入台灣銀行對帳單（假資料）〉：作業與 check 的回歸測試（每課自己一個測試檔，不改 test_regressions.py）。

grader 加的（只對寫了它的題目生效）：
  call 的 missing_call_hint  要學員自己做出來的檔（請 AI 寫的 import_bank.py）還沒有時，提示怎麼補（舊課 call 題的 missing_hint 照舊不用）。
  pytest_chaff 的 extra_files  測試要讀的資料檔（樣本對帳單 bank_a.csv、設定 settings.json）跟被測的模組放在同一個暫存資料夾，照 bytes 複製（BOM 照原樣）。
其他題目用前幾課就有的寫法：run 的 sandbox（files、probe 放課程的 bank_a.csv）、call 的 files（隱藏的髒資料對帳單）、answers、filled、git_commits。
pytest 用 uv add --dev --offline 從 uv 的快取裝（不連網；沒有快取時這幾條測試會失敗，先在任何地方 uv add --dev pytest 一次）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv 和 git。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, git, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l204"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
LID = "2-4"
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


def run_py(rel: str) -> subprocess.CompletedProcess:
    return subprocess.run([UV, "run", "--offline", "--quiet", rel], cwd=L, env=grader.child_env(), capture_output=True, text=True)


def add_pytest() -> None:
    r = uv("add", "--dev", "pytest", "--offline", "--quiet")
    if r.returncode != 0:
        raise AssertionError("uv add pytest --offline 失敗（uv 的快取裡沒有 pytest？）：" + r.stderr[-400:])


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
    add_pytest()


class Basics(unittest.TestCase):
    def test_lesson_id_forms(self):
        course = grader.course_info(COURSE)
        for raw in ("2-4", "2-04", "２－４"):
            self.assertEqual(grader.normalize_id(raw, course), "2-4")
        self.assertIn("2-4", grader.available_lessons(COURSE))

    def test_start_txt_breaks_on_comma(self):
        """1-23 的讀法：第三筆的備註有逗號，切成五段，ValueError: too many values to unpack。"""
        start()
        p = run_py("lessons/2-4/read_txt.py")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("too many values to unpack", p.stderr)
        self.assertIn("11/04 公車 15", p.stdout)

    def test_start_peek_keyerror(self):
        """起點的 peek.py 用 utf-8 讀有 BOM 的 bank_a.csv：KeyError: '交易日期'。"""
        start()
        p = run_py("lessons/2-4/peek.py")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("KeyError: '交易日期'", p.stderr)

    def test_bank_files_are_fake_and_bom(self):
        """bank_a.csv 開頭有 BOM、bank_b.csv 沒有；兩份都沒有像帳號、卡號的長串數字。"""
        a = (D / "start" / "bank_a.csv").read_bytes()
        b = (D / "start" / "bank_b.csv").read_bytes()
        self.assertTrue(a.startswith(b"\xef\xbb\xbf"))
        self.assertFalse(b.startswith(b"\xef\xbb\xbf"))
        import re
        for raw in (a, b):
            self.assertIsNone(re.search(rb"\d{8,}", raw))

    def test_answer_letters(self):
        key = json.loads((D / "answers" / "re.json").read_text(encoding="utf-8"))
        self.assertEqual([q["accept"] for q in key["questions"]], [["A"], ["B"], ["C"]])

    def test_reference_totals(self):
        """正確版：bank_a.csv 的各分類合計（影片裡手算的）；課程凍結的 AI 版本把退款當支出，日用品多 700。"""
        ns: dict = {}
        exec(compile((D / "reference" / "import_bank.py").read_text(encoding="utf-8"), "import_bank.py", "exec"), ns)
        kw = json.loads((D / "reference" / "settings.json").read_text(encoding="utf-8"))["分類關鍵字"]
        e = ns["import_statement"](D / "start" / "bank_a.csv", kw)
        self.assertEqual(ns["category_totals"](e), {"餐飲": 185, "交通": 500, "日用品": 900, "娛樂": 320})
        ai: dict = {}
        exec(compile((D / "start" / "ai_import_bank.py").read_text(encoding="utf-8"), "ai_import_bank.py", "exec"), ai)
        self.assertEqual(ai["category_totals"](ai["import_statement"](D / "start" / "bank_a.csv", kw))["日用品"], 1600)


class Ring1(unittest.TestCase):
    def setUp(self):
        start()

    def test_start_all_fail(self):
        rs = by(ev(["csv-save", "csv-read", "json", "bom", "to-int-1", "to-int-2", "bank-read"]))
        for k, r in rs.items():
            self.assertFalse(r.ok, k)
        self.assertIn("ensure_ascii=False", rs["json"].detail)
        self.assertIn("utf-8-sig", rs["bom"].detail)

    def test_reference_all_pass(self):
        for name in ("save_csv.py", "read_csv.py", "save_settings.py", "peek.py", "clean.py", "read_bank.py"):
            ref(name)
        rs = by(ev(["csv-save", "csv-read", "json", "bom", "to-int-1", "to-int-2", "bank-read"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_manual_join_fails_quotes(self):
        """自己用逗號接字串（1-23 的寫法）：ledger.csv 第三筆沒有雙引號，check 說內容不一樣。"""
        text = mine("save_csv.py").read_text(encoding="utf-8").replace(
            "# 換你寫：with open 打開 p", 'with open(p, "w", encoding="utf-8") as f:\n    f.write(",".join(FIELDS) + "\\n")\n'
            '    for e in entries:\n        f.write(f"{e[\'日期\']},{e[\'項目\']},{e[\'金額\']},{e[\'備註\']}\\n")\n# 換你寫：with open 打開 p')
        write(mine("save_csv.py"), text)
        r = by(ev(["csv-save"]))["csv-save"]
        self.assertFalse(r.ok)
        self.assertIn("ledger.csv 的內容跟應該的不一樣", r.detail)

    def test_bom_written_fails(self):
        """寫 ledger.csv 用 utf-8-sig：檔案開頭多一個 BOM，標題列對不上（照 README：寫檔用 utf-8，utf-8-sig 是讀別人的檔用的）。"""
        ref("save_csv.py")
        write(mine("save_csv.py"), mine("save_csv.py").read_text(encoding="utf-8").replace('encoding="utf-8", newline=""', 'encoding="utf-8-sig", newline=""'))
        r = by(ev(["csv-save"]))["csv-save"]
        self.assertFalse(r.ok)

    def test_to_int_strip_minus_fails(self):
        """to_int 用 re.sub(r"\\D", "", text)：1,250 過，-1,200 變成 1200 沒過。"""
        write(mine("clean.py"), mine("clean.py").read_text(encoding="utf-8").replace(
            "return int(text)   # 換你改：先拿掉千分位的逗號", 'return int(re.sub(r"\\D", "", text))'))
        rs = by(ev(["to-int-1", "to-int-2"]))
        self.assertTrue(rs["to-int-1"].ok, rs["to-int-1"].detail)
        self.assertFalse(rs["to-int-2"].ok)
        self.assertIn("1200", rs["to-int-2"].detail)

    def test_read_bank_without_skip(self):
        """to_int 修好、還沒跳過空白列：roc_date('') 丟出 ValueError（看不懂的日期）。"""
        ref("clean.py")
        r = by(ev(["bank-read"]))["bank-read"]
        self.assertFalse(r.ok)
        self.assertIn("看不懂的日期", r.detail)

    def test_re_answers(self):
        answer("re.txt", ["A", "B", "C"])
        rs = by(ev(["re"]))
        self.assertTrue(all(r.ok for r in rs.values()), [(r.id, r.detail) for r in rs.values()])
        answer("re.txt", ["B", "B", "A"])
        rs = by(ev(["re"]))
        self.assertEqual(sum(r.ok for r in rs.values()), 1)

    def test_ledger_untouched(self):
        for name in ("save_csv.py", "read_csv.py", "save_settings.py", "peek.py", "clean.py", "read_bank.py"):
            ref(name)
        before = snapshot(L)
        ev(["csv-save", "csv-read", "json", "bom", "bank-read"])
        self.assertEqual(snapshot(L), before)


class Ring3Accept(unittest.TestCase):
    def setUp(self):
        start()
        ref("settings.json")

    def test_start_test_only_count(self):
        """起點只有 test_count：正確版過；退款整筆跳過（少一筆）抓得到，退款當支出（筆數一樣）溜過去，提示講日用品多了 700。"""
        out = ev(["accept"])
        rs = by(out)
        self.assertTrue(rs["accept-wheat"].ok, rs["accept-wheat"].detail)
        self.assertFalse(rs["accept-m1"].ok)
        self.assertIn("日用品多了 700", rs["accept-m1"].detail)
        self.assertTrue(rs["accept-m2"].ok)
        self.assertIn("test_import.py 抓到 1 個壞版本，還有 1 個溜過去：", out.summaries)
        for s in out.summaries:
            self.assertLessEqual(grader._cols(s), 68, s)

    def test_answer_catches_both(self):
        write(mine("tests/test_import.py"), (D / "answers" / "test_import.py").read_text(encoding="utf-8"))
        rs = by(ev(["accept"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))
        self.assertEqual(rs["accept-m1"].note, "被 test_totals 抓到")

    def test_totals_only_catches_both(self):
        """只寫 test_totals（影片裡熊的寫法）就抓得到兩個壞版本。"""
        text = mine("tests/test_import.py").read_text(encoding="utf-8") + (
            '\n\ndef test_totals():\n    entries = import_statement(FOLDER / "bank_a.csv", KEYWORDS)\n'
            '    assert category_totals(entries) == {"餐飲": 185, "交通": 500, "日用品": 900, "娛樂": 320}\n')
        write(mine("tests/test_import.py"), text)
        rs = by(ev(["accept"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_refund_added_wrong_expectation(self):
        """手算時把退款加進去（日用品 1600）：正確版就沒過，提示期望值要再算一次。"""
        text = mine("tests/test_import.py").read_text(encoding="utf-8") + (
            '\n\ndef test_totals():\n    entries = import_statement(FOLDER / "bank_a.csv", KEYWORDS)\n'
            '    assert category_totals(entries) == {"餐飲": 185, "交通": 500, "日用品": 1600, "娛樂": 320}\n')
        write(mine("tests/test_import.py"), text)
        r = by(ev(["accept"]))["accept-wheat"]
        self.assertFalse(r.ok)
        self.assertIn("test_totals 在正確版上就沒過", r.detail)

    def test_total_sum_misses_refund_skip(self):
        """只比全部加起來的總數（1905）：退款當支出（2605）抓得到，退款整筆跳過（2255）也抓得到；只看筆數就溜過 m1。"""
        text = mine("tests/test_import.py").read_text(encoding="utf-8") + (
            '\n\ndef test_totals():\n    entries = import_statement(FOLDER / "bank_a.csv", KEYWORDS)\n'
            '    assert sum(category_totals(entries).values()) == 1905\n')
        write(mine("tests/test_import.py"), text)
        rs = by(ev(["accept"]))
        self.assertTrue(rs["accept-m1"].ok and rs["accept-m2"].ok)

    def test_extra_files_dont_touch_ledger(self):
        write(mine("tests/test_import.py"), (D / "answers" / "test_import.py").read_text(encoding="utf-8"))
        before = snapshot(L)
        ev(["accept"])
        self.assertEqual(snapshot(L), before)


class Ring3Import(unittest.TestCase):
    IDS = ["hidden-1", "hidden-2", "hidden-3", "totals"]

    def setUp(self):
        start()

    def test_missing_hint(self):
        r = by(ev(["hidden-1"]))["hidden-1"]
        self.assertFalse(r.ok)
        self.assertIn("cp lessons/2-4/ai_import_bank.py", r.detail)

    def test_frozen_ai_fails_refunds(self):
        """課程凍結的 AI 版本：有退款的兩份隱藏對帳單沒過（負號被拿掉），只有標題列的、category_totals 過。"""
        shutil.copyfile(mine("ai_import_bank.py"), mine("import_bank.py"))
        rs = by(ev(self.IDS))
        self.assertFalse(rs["hidden-1"].ok)
        self.assertFalse(rs["hidden-2"].ok)
        self.assertTrue(rs["hidden-3"].ok, rs["hidden-3"].detail)
        self.assertTrue(rs["totals"].ok, rs["totals"].detail)
        self.assertIn("1200", rs["hidden-1"].detail)
        self.assertIn("check 交給它的檔案", rs["hidden-1"].detail)

    def test_fixed_ai_passes(self):
        """熊在影片裡改的那一行（parse_amount 改成只拿掉逗號）：四題全過。"""
        text = mine("ai_import_bank.py").read_text(encoding="utf-8").replace('return int(re.sub(r"\\D", "", text))', 'return int(text.replace(",", ""))')
        write(mine("import_bank.py"), text)
        rs = by(ev(self.IDS))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_reference_passes(self):
        ref("import_bank.py")
        rs = by(ev(self.IDS))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))

    def test_one_bank_only_fails_hidden2(self):
        """只認得第一家的欄位名稱：另一家銀行（消費日、說明、交易金額）那一題沒過。"""
        text = (D / "reference" / "import_bank.py").read_text(encoding="utf-8").replace('"日期": ["交易日期", "消費日"]', '"日期": ["交易日期"]')
        write(mine("import_bank.py"), text)
        rs = by(ev(self.IDS))
        self.assertTrue(rs["hidden-1"].ok)
        self.assertFalse(rs["hidden-2"].ok)

    def test_plain_utf8_fails_bom(self):
        """用 utf-8 讀（沒讀掉 BOM）：有 BOM 的那兩份都沒過。"""
        text = (D / "reference" / "import_bank.py").read_text(encoding="utf-8").replace('encoding="utf-8-sig"', 'encoding="utf-8"')
        write(mine("import_bank.py"), text)
        rs = by(ev(self.IDS))
        self.assertFalse(rs["hidden-1"].ok)
        self.assertTrue(rs["hidden-2"].ok)


class Ring3Save(unittest.TestCase):
    def setUp(self):
        start()

    def tearDown(self):
        if (L / ".git").exists():
            shutil.rmtree(L / ".git")

    def test_saved_before_and_after(self):
        fresh_repo()
        save("交辦前")
        ref("import_bank.py")
        write(mine("tests/test_import.py"), (D / "answers" / "test_import.py").read_text(encoding="utf-8"))
        save("匯入對帳單")
        r = by(ev(["saved"]))["saved"]
        self.assertTrue(r.ok, r.detail)

    def test_not_saved_before(self):
        fresh_repo()
        write(L / "README.md", "# 帳本\n")
        save("第一個存檔點")
        r = by(ev(["saved"]))["saved"]
        self.assertFalse(r.ok)

    def test_forms(self):
        fill("pandas.md", {"家教的建議：": "用 pandas 的 read_csv", "要不要用 pandas：": "不用", "理由：": "要多裝好幾個套件，還沒學，csv 就做得到"})
        fill("decision.md", {"它跑了什麼指令：": "uv run pytest", "uv run pytest 的結果：": "1 failed", "哪一類的合計不對、為什麼：": "日用品，負號被拿掉",
                             "我改了哪一行：": "parse_amount", "收不收，為什麼：": "改完收"})
        rs = by(ev(["pandas", "decision"]))
        for k, r in rs.items():
            self.assertTrue(r.ok, (k, r.detail))


if __name__ == "__main__":
    unittest.main()
