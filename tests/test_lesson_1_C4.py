"""1-C4〈檢核站 4〉：交卷、訂正、矯正包、卷 B 的回歸測試（照 test_lesson_1_C3.py）。

檢核站 4 跟前三站用同一套（check.py 的 cmd_checkpoint、start_checkpoint）：
  - 13 題、第一次交卷過 11 題以上算過；之後再打是訂正，不改成績；還有題目空著不算交卷（--submit 例外）。
  - 第一部分 trace.txt 追蹤函式呼叫 6 題、第二部分 except.txt 找出 except 的問題 3 題（對答；選擇題 strict_choice、一行好幾個值的 keep_spaces）；
    第三部分 write.py 的 file_total 4 題：func_shape（with open、encoding="utf-8"、return；grader 1-C4 加的 ast_require）＋
    call 三次（grader 1-C4 加的 files：check 在暫存資料夾寫好三個帳本檔、交完整路徑給函式；三筆有換行 315、兩筆最後一行沒換行 510、空的 0）。
  - 卷 B 放在 lessons/1-C4/B/，卷 A 交卷的隔天以後才能 start；矯正包對照表卷 A、卷 B 共用（題目 id 一樣）。
全部寫在 PLUSFORM_TEST_WS 底下，不寫課程資料夾、不寫真的家目錄。需要 uv（帳本是真的 uv 專案）。
"""

from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from _support import COURSE, UV, WS, fresh_dir, make_env, run_check, snapshot, uv_ledger

from engine import grader  # noqa: E402

BASE = WS / "l1c4"
L = BASE / "ledger 帳本"   # 路徑有空白和中文
D = COURSE / "lessons" / "1-C4"
DAY1, DAY1_LATE, DAY2 = "2026-12-02T19:00:00+08:00", "2026-12-02T23:30:00+08:00", "2026-12-03T20:00:00+08:00"
RIGHT_A = ["收到 3", "15 0 None", "1 2 2", "[100, 30]", "B", "A"]
RIGHT_B = ["付了 10", "25 0 None", "1 2 3", "[40, 25, 60]", "C", "B"]
EXC_A, EXC_B = ["合計 200", "B", "C"], ["一共 8 份", "C", "A"]
WRITE_A = (D / "reference" / "write.py").read_text(encoding="utf-8")
WRITE_B = (D / "B" / "reference" / "write.py").read_text(encoding="utf-8")
START_A = (D / "start" / "write.py").read_text(encoding="utf-8")
START_B = (D / "B" / "start" / "write.py").read_text(encoding="utf-8")
WRITE_IDS = ["write-shape", "write-basic", "write-nonl", "write-empty"]
REM = json.loads((D / "remedial.json").read_text(encoding="utf-8"))
T_DEF = REM["topics"]["default"]["where"][0]["time"]     # 1-19 預設值用 [] 的陷阱（時間碼照各課時間軸重算，那幾課重配就會變，測試照 remedial.json 比）
T_OPEN = REM["topics"]["open"]["where"][0]["time"]       # 1-23 w 和 a、Windows 的預設編碼
T_LAST = REM["topics"]["lastline"]["where"][0]["time"]   # 1-23 寫進檔案、讀回來

# 第三部分常見的寫法（函式內容，接在 docstring 下面；卷 B 的 item 換成 way 也一樣）
BODY = {
    "rstrip": ("    total = 0\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f:\n            d, item, amount = line.rstrip(\"\\n\").split(\",\")\n"
               "            total += int(amount)\n    return total\n"),
    "nostrip": ("    total = 0\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f:\n            parts = line.split(\",\")\n"
                "            total = total + int(parts[2])\n    return total\n"),
    "strip_all": ("    total = 0\n    with open(path, encoding=\"UTF-8\") as f:\n        for line in f:\n            d, item, amount = line.strip().split(\",\")\n"
                  "            total += int(amount)\n    return total\n"),
    "cut_last": ("    total = 0\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f:\n            d, item, amount = line[:-1].split(\",\")\n"
                 "            total += int(amount)\n    return total\n"),
    "read_split": ("    total = 0\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f.read().split(\"\\n\"):\n            d, item, amount = line.split(\",\")\n"
                   "            total += int(amount)\n    return total\n"),
    "first_line": "    with open(path, encoding=\"utf-8\") as f:\n        line = f.readline()\n    d, item, amount = line.rstrip(\"\\n\").split(\",\")\n    return int(amount)\n",
    "no_int": ("    total = \"\"\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f:\n            d, item, amount = line.rstrip(\"\\n\").split(\",\")\n"
               "            total += amount\n    return total\n"),
    "no_encoding": ("    total = 0\n    with open(path) as f:\n        for line in f:\n            d, item, amount = line.rstrip(\"\\n\").split(\",\")\n"
                    "            total += int(amount)\n    return total\n"),
    "no_with": ("    total = 0\n    f = open(path, encoding=\"utf-8\")\n    for line in f:\n        d, item, amount = line.rstrip(\"\\n\").split(\",\")\n"
                "        total += int(amount)\n    f.close()\n    return total\n"),
    "print_only": ("    total = 0\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f:\n            d, item, amount = line.rstrip(\"\\n\").split(\",\")\n"
                   "            total += int(amount)\n    print(total)\n"),
    "hardcode": "    with open(path, encoding=\"utf-8\") as f:\n        pass\n    return 315\n",
    # Codex 影片第一輪：金額用 float 加，交回 315.0（strict_type 擋）；encoding 用變數交進去（讀得到，可是這一題看寫法）
    "float": ("    total = 0\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f:\n            d, item, amount = line.rstrip(\"\\n\").split(\",\")\n"
              "            total += float(amount)\n    return total\n"),
    "enc_var": ("    total = 0\n    enc = \"utf-8\"\n    with open(path, encoding=enc) as f:\n        for line in f:\n            d, item, amount = line.rstrip(\"\\n\").split(\",\")\n"
                "            total += int(amount)\n    return total\n"),
    "here_path": ("    total = 0\n    p = Path(__file__).parent / path\n    with open(p, encoding=\"utf-8\") as f:\n        for line in f:\n"
                  "            d, item, amount = line.rstrip(\"\\n\").split(\",\")\n            total += int(amount)\n    return total\n"),
}
# 預設值 [] 存金額：第二次呼叫就錯（def 那一行不一樣，整個函式換掉）
KEEP_A = ("def file_total(path, seen=[]):\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f:\n"
          "            d, item, amount = line.rstrip(\"\\n\").split(\",\")\n            seen.append(int(amount))\n    return sum(seen)\n")
WANT = {   # [寫法, 三筆, 最後一行沒換行, 空的]
    "rstrip": [True, True, True, True], "nostrip": [True, True, True, True], "strip_all": [True, True, True, True],
    "cut_last": [True, True, False, True], "read_split": [True, False, True, False], "first_line": [True, False, False, False],
    "no_int": [True, False, False, False], "no_encoding": [False, True, True, True], "no_with": [False, True, True, True],
    "print_only": [False, False, False, False], "hardcode": [True, True, False, False], "here_path": [True, True, True, True],
    "float": [True, False, False, True], "enc_var": [False, True, True, True],
}


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def with_body(start: str, body: str, var: str = "item") -> str:
    """起點檔 docstring 下面接上函式內容（卷 B 的拆包名字換成 way）。"""
    head, sep, tail = start.partition('    """\n\n\nif __name__')
    assert sep, "起點檔的樣子變了"
    return head + '    """\n' + body.replace("item", var) + '\n\nif __name__' + tail


def answer(lid: str, fname: str, answers: list[str]) -> None:
    p = L / "lessons" / lid / fname
    it = iter(answers)
    p.write_text("\n".join(("答：" + next(it)) if ln.startswith("答：") else ln
                           for ln in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def fresh_start(lid: str = "1-C4") -> Path:
    dest = L / "lessons" / lid
    if dest.exists():
        shutil.rmtree(dest)
    src = D / ("B/start" if lid.endswith("B") else "start")
    shutil.copytree(src, dest)
    return dest


def ev(lid: str, ids: list[str] | None = None) -> grader.Outcome:
    les = grader.load_lesson(lid, COURSE)
    return grader.evaluate(les, L, only=None if ids is None else [c for c in les.checks if c["id"] in ids])


def part(out: grader.Outcome, rid: str) -> grader.Result:
    return next(r for r in out.results if r.id == rid)


def oks(out: grader.Outcome) -> list[bool]:
    return [r.ok for r in out.results]


RABBIT_WRITE = BODY["no_encoding"].replace('line.rstrip("\\n")', "line[:-1]")   # 果凍兔：open 沒寫 encoding（Mac 上讀得到）＋用 [:-1] 拿掉換行


def setUpModule():
    if UV is None:
        raise unittest.SkipTest("需要 uv")
    BASE.mkdir(parents=True, exist_ok=True)
    uv_ledger(L)


class Grading(unittest.TestCase):
    """grader：卷 A、卷 B 的正確版全過、起點不過；追蹤和找問題的寫法與常見的錯；手寫的各種寫法；暫存檔不碰帳本。"""

    def setUp(self):
        fresh_start("1-C4")

    def test_ids_and_paper_b_folder(self):
        info = grader.course_info(COURSE)
        for raw, want in (("1-C4", "1-C4"), ("1-c4", "1-C4"), ("1-C4B", "1-C4B"), ("1-c4b", "1-C4B"), ("1-C4-B", "1-C4B")):
            self.assertEqual(grader.normalize_id(raw, info), want, raw)
        b = grader.load_lesson("1-C4B", COURSE)
        self.assertEqual(b.dir, D / "B")
        self.assertEqual(b.meta["paper_of"], "1-C4")
        self.assertNotIn("1-C4B", grader.available_lessons(COURSE))
        self.assertIn("1-C4", grader.available_lessons(COURSE))

    def test_reference_answers_pass_all_thirteen_and_start_does_not(self):
        out = ev("1-C4")
        self.assertEqual(out.total, 13)
        self.assertFalse(any(r.ok for r in out.results), [(r.id, r.ok) for r in out.results])
        answer("1-C4", "trace.txt", RIGHT_A)
        answer("1-C4", "except.txt", EXC_A)
        write(L / "lessons/1-C4/write.py", WRITE_A)
        out = ev("1-C4")
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])
        stages = [r.stage for r in out.results]
        self.assertEqual((stages.count("第一部分 追蹤"), stages.count("第二部分 找問題"), stages.count("第三部分 手寫")), (6, 3, 4))

    def test_paper_b_reference_passes_and_start_does_not(self):
        fresh_start("1-C4B")
        out = ev("1-C4B")
        self.assertFalse(any(r.ok for r in out.results))
        answer("1-C4B", "trace.txt", RIGHT_B)
        answer("1-C4B", "except.txt", EXC_B)
        write(L / "lessons/1-C4B/write.py", WRITE_B)
        out = ev("1-C4B")
        self.assertEqual(out.total, 13)
        self.assertTrue(all(r.ok for r in out.results), [(r.id, r.detail) for r in out.results])

    def test_trace_spacing_choices_and_common_mistakes(self):
        answer("1-C4", "trace.txt", ["收到3", "15  0  none", "1 2 2", "[100,30]", "b. 3 行", "A. 2.5 元"])
        self.assertEqual(oks(ev("1-C4", ["trace"])), [True] * 6)
        # 常見的錯：沒用關鍵字的 tip、以為函式裡的 total 改到外面／show 交回印的字、以為預設值每次都是新的、以為 week 不會被改、
        # 以為 import 不會跑 money.py 的 print（或連 __main__ 底下也跑）、以為型別提示會擋（或會換成整數）
        answer("1-C4", "trace.txt", ["收到 11", "15 15 None", "1 1 2", "[100]", "A", "C"])
        self.assertEqual(oks(ev("1-C4", ["trace"])), [False] * 6)
        answer("1-C4", "trace.txt", RIGHT_A[:1] + ["150None", "122"] + RIGHT_A[3:4] + ["C", "B"])
        out = ev("1-C4", ["trace"])
        self.assertEqual([part(out, f"trace-t{i}").ok for i in (2, 3, 5, 6)], [False] * 4)
        answer("1-C4", "trace.txt", RIGHT_A[:4] + ["B 或 C", "A、C"])
        out = ev("1-C4", ["trace"])
        self.assertFalse(part(out, "trace-t5").ok)
        self.assertIn("只能選一個", part(out, "trace-t5").detail)

    def test_except_catches_swallowed_and_too_broad(self):
        answer("1-C4", "except.txt", ["合計200", "b", "C. to_yuan 裡不寫"])
        self.assertEqual(oks(ev("1-C4", ["exc"])), [True] * 3)
        # 以為錯會跳出來（沒看出吞掉）、以為打錯字看得到（沒看出接太廣）、只寫明 ValueError 還是交回 0
        answer("1-C4", "except.txt", ["合計 115", "C", "A"])
        out = ev("1-C4", ["exc"])
        self.assertEqual(oks(out), [False] * 3)
        self.assertIn("交回什麼", part(out, "exc-e1").detail)
        answer("1-C4", "except.txt", ["合計 200", "A", "B"])
        self.assertEqual(oks(ev("1-C4", ["exc"])), [True, False, False])
        fresh_start("1-C4B")
        answer("1-C4B", "except.txt", ["一共8份", "c", "A"])
        self.assertEqual(oks(ev("1-C4B", ["exc"])), [True] * 3)
        answer("1-C4B", "except.txt", ["一共 6 份", "A", "B"])
        self.assertEqual(oks(ev("1-C4B", ["exc"])), [False] * 3)

    def test_write_ways_on_three_temp_files(self):
        for name, want in WANT.items():
            write(L / "lessons/1-C4/write.py", with_body(START_A, BODY[name]))
            self.assertEqual(oks(ev("1-C4", WRITE_IDS)), want, name)
        write(L / "lessons/1-C4/write.py", START_A.replace("def file_total(path):", KEEP_A.split("\n")[0]).replace(
            '    """\n\n\nif', '    """\n' + "\n".join(KEEP_A.split("\n")[1:]) + '\n\nif'))
        self.assertEqual(oks(ev("1-C4", WRITE_IDS)), [True, True, False, False])   # 同一個程序照順序呼叫：第二次就錯
        # 說明裡看得出交給它的是哪一個檔
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["cut_last"]))
        r = part(ev("1-C4", ["write-nonl"]), "write-nonl")
        self.assertIn("應該回傳510", r.detail.replace(" ", ""))
        self.assertIn("你的回傳456", r.detail.replace(" ", ""))
        self.assertIn("（最後一行後面沒有換行）", r.detail)
        self.assertIn("12/02,咖啡,60", r.detail)
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["read_split"]))
        r = part(ev("1-C4", ["write-empty"]), "write-empty")
        self.assertIn("空的檔案（一個字都沒有）", r.detail)
        self.assertIn("ValueError", r.detail)
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["no_encoding"]))
        r = part(ev("1-C4", ["write-shape"]), "write-shape")
        self.assertIn('encoding="utf-8"', r.detail)
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["float"]))
        r = part(ev("1-C4", ["write-basic"]), "write-basic")
        self.assertIn("型別不一樣：應該是整數 int，你交回的是小數 float", r.detail)
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["enc_var"]))
        self.assertIn('直接寫 encoding="utf-8"', part(ev("1-C4", ["write-shape"]), "write-shape").detail)
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["no_with"]))
        self.assertIn("with 後面", part(ev("1-C4", ["write-shape"]), "write-shape").detail)
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["print_only"]))
        r = part(ev("1-C4", ["write-shape", "write-basic"]), "write-basic")
        self.assertIn("回傳 None，常常是用了 print", r.detail)
        # 只看函式裡面：最下面 if __name__ 那幾行的 open 不算
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["rstrip"]) + '    with open("x.txt") as f:\n        pass\n')
        self.assertTrue(part(ev("1-C4", ["write-shape"]), "write-shape").ok)

    def test_paper_b_write_catches_the_same_mistakes(self):
        fresh_start("1-C4B")
        for name, want in WANT.items():
            body = BODY[name].replace("315", "390")
            write(L / "lessons/1-C4B/write.py", with_body(START_B, body, "way"))
            self.assertEqual(oks(ev("1-C4B", WRITE_IDS)), want, name)
        write(L / "lessons/1-C4B/write.py", with_body(START_B, BODY["cut_last"], "way"))
        self.assertIn("你的回傳1204", part(ev("1-C4B", ["write-nonl"]), "write-nonl").detail.replace(" ", ""))

    def test_temp_files_do_not_touch_the_ledger(self):
        write(L / "lessons/1-C4/write.py", with_body(START_A, BODY["rstrip"]))
        before = snapshot(L / "lessons/1-C4")
        top = sorted(p.name for p in L.iterdir())
        self.assertTrue(all(oks(ev("1-C4", WRITE_IDS))))
        self.assertEqual(snapshot(L / "lessons/1-C4"), before)
        self.assertEqual(sorted(p.name for p in L.iterdir()), top)
        self.assertFalse(any((L / "lessons/1-C4" / n).exists() for n in ("a3.txt", "b2.txt", "c0.txt")))

    def test_sample_file_prints_315_and_390(self):
        env = grader.Env(L)
        write(L / "lessons/1-C4/write.py", WRITE_A)
        p = env.run_file(L / "lessons/1-C4/write.py")
        self.assertEqual(p.stdout.strip(), "315", p.stderr)
        fresh_start("1-C4B")
        write(L / "lessons/1-C4B/write.py", WRITE_B)
        p = env.run_file(L / "lessons/1-C4B/write.py")
        self.assertEqual(p.stdout.strip(), "390", p.stderr)

    def test_remedial_key_matches_every_check(self):
        rem = json.loads((D / "remedial.json").read_text(encoding="utf-8"))
        for lid in ("1-C4", "1-C4B"):
            les = grader.load_lesson(lid, COURSE)
            ids = [r.id for r in grader.plan(les, L)]
            self.assertEqual(sorted(ids), sorted(rem["items"]), lid)
        for t in rem["topics"].values():
            self.assertTrue((D / "practice" / t["practice"]).is_file(), t["practice"])
            for w in t["where"]:
                self.assertRegex(w["time"], r"^\d+:\d\d$")


class Flow(unittest.TestCase):
    """check.py：start、交卷、訂正、矯正包、卷 B、status。"""

    @classmethod
    def setUpClass(cls):
        cls.home = fresh_dir("l1c4_home")

    def setUp(self):
        for lid in ("1-C4", "1-C4B"):
            d = L / "lessons" / lid
            if d.exists():
                shutil.rmtree(d)
        if (L / ".check").exists():
            shutil.rmtree(L / ".check")
        r = run_check(["setup", str(L)], make_env(self.home))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def run_(self, args, now):
        return run_check(args, make_env(self.home, now=now))

    def rabbit_paper_a(self):
        """果凍兔：追蹤第 3 題以為預設值每次都是新的（1 1 2）、找問題全對、write.py 沒寫 encoding＋用 [:-1] 拿掉換行 → 10／13。"""
        answer("1-C4", "trace.txt", RIGHT_A[:2] + ["1 1 2"] + RIGHT_A[3:])
        answer("1-C4", "except.txt", EXC_A)
        write(L / "lessons/1-C4/write.py", with_body(START_A, RABBIT_WRITE))

    def test_start_asks_prediction_and_unfinished_is_not_a_submission(self):
        before = snapshot(COURSE)
        r = self.run_(["start", "1-C4", "--predict", "11"], DAY1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for f in ("except.txt", "sample.txt", "trace.txt", "write.py"):
            self.assertIn(f"+ lessons/1-C4/{f}", r.stdout)
        self.assertIn("記下來了：開始前你猜會過 11／13 題。交卷時會再問一次。", r.stdout)
        self.assertIn("參考時間 30 分鐘（只記錄，不擋你）", r.stdout)
        self.assertIn("uv run check.py 1-C4（交卷）", r.stdout)
        for line in r.stdout.splitlines():   # 影片錄的是這一段：70 欄寫得完（中文算兩欄）
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        self.assertEqual((L / "lessons/1-C4/sample.txt").read_bytes(), (D / "start/sample.txt").read_bytes())
        r = self.run_(["1-C4", "--predict", "12"], DAY1)
        self.assertEqual(r.returncode, 1)
        self.assertIn("trace.txt 第 1、2、3、4、5、6 題還沒寫", r.stdout)
        self.assertIn("except.txt 第 1、2、3 題還沒寫", r.stdout)
        self.assertIn("write.py 還沒改", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertNotIn("submitted", prog["lessons"]["1-C4"])
        self.assertEqual(snapshot(COURSE), before)

    def test_fail_writes_the_remedial_pack_and_redo_does_not_change_the_score(self):
        self.run_(["start", "1-C4", "--predict", "11"], DAY1)
        self.rabbit_paper_a()
        r = self.run_(["1-C4", "--predict", "12", "--no-review"], "2026-12-02T19:29:00+08:00")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("結果：過了 10／13 題（11 題以上算過）", out)
        self.assertIn("✗ 第一部分 追蹤  5／6", out)
        self.assertIn("✓ 第二部分 找問題  3／3", out)
        self.assertIn("✗ 第三部分 手寫  2／4", out)
        self.assertIn("你猜 12 題，實際過了 10 題：高估了 2 題", out)
        self.assertIn("（開始前你猜 11 題，做完猜 12 題，實際 10 題。）", out)
        self.assertIn("這次沒過。矯正包在帳本的 lessons/1-C4/矯正包.md：", out)
        self.assertIn(f"  追蹤第 3 題 → 1-19 影片 {T_DEF} 起", out)
        self.assertIn(f"  手寫：with open 和 encoding → 1-23 影片 {T_OPEN} 起", out)
        self.assertIn(f"  手寫：最後一行沒換行 → 1-23 影片 {T_LAST} 起", out)
        self.assertIn("練完，明天以後考卷 B：uv run check.py start 1-C4B", out)
        self.assertLessEqual(len(out.splitlines()), 16)   # 影片錄的是這一段：一個畫面 17 列（含指令那一列）
        for line in out.splitlines():
            self.assertLessEqual(sum(2 if ord(c) > 0x2E7F else 1 for c in line), 70, line)
        readme = (D / "README.md").read_text(encoding="utf-8")
        for line in out.splitlines()[1:]:   # README 第 4 節的成品示範跟真的印出來的一樣
            if line.strip() and "大約" not in line:
                self.assertIn(line, readme)
        pack = (L / "lessons/1-C4/矯正包.md").read_text(encoding="utf-8")
        self.assertIn("正確答案：1 2 2", pack)
        self.assertIn(f"1-19〈函式（下）：預設值、關鍵字參數、範圍〉{T_DEF} 起", pack)
        self.assertIn(f"1-23〈檔案讀寫：關掉程式，帳還在〉{T_OPEN} 起", pack)
        self.assertIn("（最後一行後面沒有換行）", pack)
        self.assertIn("12/3 起", pack)
        self.assertEqual(sorted(p.name for p in (L / "lessons/1-C4/practice").iterdir()), ["p_default.py", "p_lastline.py", "p_open.py"])
        r = self.run_(["1-C4", "--no-review"], "2026-12-02T19:40:00+08:00")
        self.assertIn("（這是訂正：成績照 12/2 第一次交卷算，過了 10／13 題。）", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-C4"]["submitted"]["passed"], 10)
        self.assertNotIn("first_pass", prog["lessons"]["1-C4"])
        rows = [json.loads(x) for x in (L / ".check/attempts.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([a["predicted"] for a in rows], [12, None])   # 訂正不問預測、不進校準曲線

    def test_paper_b_waits_for_the_next_day_and_passing_b_passes_the_checkpoint(self):
        r = self.run_(["start", "1-C4B"], DAY1)
        self.assertIn("要等卷 A 交卷以後才能考", r.stdout)
        self.run_(["start", "1-C4", "--predict", "11"], DAY1)
        self.rabbit_paper_a()
        self.run_(["1-C4", "--predict", "12", "--no-review"], "2026-12-02T19:29:00+08:00")
        r = self.run_(["start", "1-C4B", "--predict", "11"], DAY1_LATE)
        self.assertEqual(r.returncode, 1)
        self.assertIn("卷 B 要隔天以後才能考（你在 12/2 交了卷 A）", r.stdout)
        self.assertFalse((L / "lessons/1-C4B").exists())
        r = self.run_(["start", "1-c4b", "--predict", "11"], DAY2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("+ lessons/1-C4B/write.py", r.stdout)
        answer("1-C4B", "trace.txt", RIGHT_B[:5] + ["A"])
        answer("1-C4B", "except.txt", EXC_B)
        write(L / "lessons/1-C4B/write.py", WRITE_B)
        r = self.run_(["1-C4B", "--predict", "12", "--no-review"], "2026-12-03T20:25:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 12／13 題（11 題以上算過）", r.stdout)
        self.assertIn("✓ 過了！檢核站 4 通過。", r.stdout)
        self.assertIn("錯的那 1 題，矯正包一樣寫好了：帳本的 lessons/1-C4B/矯正包.md", r.stdout)
        prog = json.loads((L / ".check/progress.json").read_text(encoding="utf-8"))
        self.assertEqual(prog["lessons"]["1-C4"]["passed_via"], "B")
        r = self.run_(["status"], "2026-12-03T20:30:00+08:00")
        self.assertIn("✓ 1-C4 檢核站 4　12/3 通過；卷 A 12/2 交卷 10／13（沒過）；卷 B 12/3 交卷 12／13", r.stdout)
        self.assertIn("1-C4 交卷：開始前猜 11、做完猜 12、實際 10／13", r.stdout)

    def test_pass_on_paper_a_and_submit_flag(self):
        self.run_(["start", "1-C4", "--predict", "13"], DAY1)
        answer("1-C4", "trace.txt", RIGHT_A[:5] + [""])
        answer("1-C4", "except.txt", EXC_A)
        write(L / "lessons/1-C4/write.py", WRITE_A)
        r = self.run_(["1-C4", "--predict", "13", "--no-review"], "2026-12-02T19:20:00+08:00")
        self.assertIn("trace.txt 第 6 題還沒寫", r.stdout)
        r = self.run_(["1-C4", "--predict", "13", "--submit", "--no-review"], "2026-12-02T19:20:00+08:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("結果：過了 12／13 題", r.stdout)
        self.assertIn("✓ 過了！檢核站 4 通過。", r.stdout)
        r = self.run_(["start", "1-C4B"], DAY2)
        self.assertIn("就過了檢核站 4，卷 B 不用考", r.stdout)


if __name__ == "__main__":
    unittest.main()
