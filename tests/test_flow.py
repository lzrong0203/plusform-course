"""完整流程：setup → 0-4 → 0-5 → 1-9 過與不過 → 特殊作答 → 回顧到期 → Lv0 關卡太快全對 → status。

在 PLUSFORM_TEST_WS 底下建假的家目錄和假的帳本，用 PLUSFORM_NOW 假裝是不同天。
需要 uv（帳本是真的 uv 專案，學員的程式在帳本的 Python 3.13 裡跑）和 git（0-C 要讀存檔點）。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from _support import COURSE, UV, fresh_dir, git, make_env, run_check, snapshot

DAY1 = "2026-11-10T09:00:00+08:00"
DECOY = "0-C-保險箱"


def at(day: int, hhmm: str) -> str:
    return f"2026-11-{9 + day:02d}T{hhmm}:00+08:00"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_0_4_tree(base: Path) -> None:
    for d in ("data/receipts", "notes", "practice"):
        (base / d).mkdir(parents=True, exist_ok=True)
    for f in ("notes/todo.txt", "notes/hello_copy.txt", "practice/hello.txt", "practice/final.txt"):
        (base / f).touch()


def fill_answers(path: Path, answers: list[str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    it = iter(answers)
    out = []
    for line in lines:
        if line.strip().startswith("答："):
            line = "答：" + next(it)
        out.append(line)
    write(path, "\n".join(out) + "\n")


@unittest.skipIf(UV is None or shutil.which("git") is None, "需要 uv 和 git")
class FullFlow(unittest.TestCase):
    maxDiff = None

    def test_full_flow(self):
        before = snapshot(COURSE)
        home = fresh_dir("flow_home")
        ledger = home / "code" / "ledger"
        ledger.mkdir(parents=True)
        cfg_file = home / ".config" / "plusform-course" / "config.json"

        def check(args, now, stdin=""):
            return run_check(args, make_env(home, now), stdin)

        # ---------- 0-4 第①圈＋ 0-5 第①圈：學員自己做的部分 ----------
        build_0_4_tree(ledger)
        env = make_env(home, DAY1)
        subprocess.run([UV, "init", "--no-package", "--vcs", "none", "--python", "3.13", "--quiet"], cwd=ledger, env=env, check=True)
        subprocess.run([UV, "python", "pin", "3.13", "--quiet"], cwd=ledger, env=env, check=True)
        self.assertFalse((ledger / ".git").exists(), "--vcs none 不該建 git")

        with self.subTest("還沒 setup"):
            r = check(["0-5", "--predict", "3"], at(1, "09:00"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("還不知道你的帳本在哪裡", r.stdout)

        with self.subTest("setup 拒絕放在課程資料夾裡、拒絕家目錄"):
            r = check(["setup", str(COURSE / "lessons")], at(1, "09:00"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("帳本不能放在課程資料夾裡面", r.stdout)
            r = check(["setup", str(home)], at(1, "09:00"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("不能直接用家目錄", r.stdout)
            self.assertFalse(cfg_file.exists())

        with self.subTest("setup"):
            r = check(["setup", str(ledger)], at(1, "09:01"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("記好了", r.stdout)
            cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
            self.assertEqual(Path(cfg["ledger"]), ledger.resolve())
            self.assertTrue((ledger / ".check" / "README.txt").is_file())

        # ---------- 0-4 ----------
        with self.subTest("0-4 全過"):
            r = check(["start", "0-4"], at(1, "09:02"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            work = ledger / "lessons" / "0-4"
            self.assertTrue((work / "permissions.txt").is_file())
            self.assertTrue((work / "agent_setup.txt").is_file())
            self.assertFalse((work / "agent_setup.sh").exists(), "會刪東西的腳本不該存成 .sh 發給學員")
            self.assertIn(f"open -e {ledger}/lessons/0-4/permissions.txt", r.stdout)
            fill_answers(work / "permissions.txt", ["允許", "允許", "拒絕", "允許", "允許", "拒絕"])
            write(work / "checks.txt", "budget/2026-11/food.txt\nbudget/2026-11/bus.txt\nbudget/todo_copy.txt\nnotes/todo.txt\n")
            r = check(["0-4", "--predict", "8"], at(1, "09:05"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("全部 12 題都過了", r.stdout)
            self.assertIn("你的檢查把 3 個壞版本全部抓到了", r.stdout)

        with self.subTest("0-4 第③圈漏掉 rm -rf"):
            write(ledger / "lessons" / "0-4" / "checks.txt", "budget/2026-11/food.txt\nbudget/todo_copy.txt\nbudget/2026-11/bus.txt\n")
            r = check(["0-4", "--predict", "9"], at(1, "09:06"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("還有 1 個溜過去：\n    ・藏起來的 rm -rf", r.stdout)
            write(ledger / "lessons" / "0-4" / "checks.txt", "budget/2026-11/food.txt\nbudget/2026-11/bus.txt\nbudget/todo_copy.txt\nnotes/todo.txt\n")

        # ---------- 0-5 ----------
        with self.subTest("0-5 還沒作答：只顯示第一個沒過的，說清楚要改哪個檔"):
            check(["start", "0-5"], at(1, "09:10"))
            r = check(["0-5", "--predict", "13"], at(1, "09:11"))
            self.assertEqual(r.returncode, 1)
            self.assertEqual(r.stdout.count("✗ 第一個沒過的"), 1)
            self.assertIn("✗ 第一個沒過的：對答第 1 題（錯誤訊息「zsh: command not found: uv」）", r.stdout)
            self.assertIn("還沒作答：打開帳本裡的 lessons/0-5/error_match.txt，在第 1 題的「答：」後面寫A、B 或 C", r.stdout)
            self.assertIn("加 --all", r.stdout)
            r = check(["0-5", "--predict", "13", "--all"], at(1, "09:12"))
            self.assertIn("還有 3 行有「？」沒填完", r.stdout)

        with self.subTest("0-5 全過（uv 專案、3.13、main.py、不是系統 Python、doctor 抓壞版本）"):
            work = ledger / "lessons" / "0-5"
            fill_answers(work / "error_match.txt", ["B. PATH 還沒更新", "a", "C"])
            write(work / "doctor_expected.txt", "Python版本：3.13\n在帳本的環境裡： 是\n用的是系統 Python:否\n")
            r = check(["env", "--predict", "13"], at(1, "09:20"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("全部 13 題都過了", r.stdout)

        # ---------- 1-9 ----------
        work = ledger / "lessons" / "1-9"
        with self.subTest("1-9 起點檔：不過，只顯示第一個錯，校準落差大要寫一句，提示先不亮"):
            r = check(["start", "1-9"], at(1, "10:00"))
            for name in ("trace.txt", "budget_light.py", "ai_review.txt", "judgment_card.md", "bmi.py", "checks_bmi.py"):
                self.assertTrue((work / name).is_file(), name)
            r = check(["1-9", "--predict", "19"], at(1, "10:00"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("結果：過了 1／19 題", r.stdout)
            self.assertIn("✗ 第一個沒過的：預算燈號", r.stdout)
            self.assertIn("餵給它的輸入：500、1000", r.stdout)
            self.assertIn("還有 17 題沒過", r.stdout)
            self.assertIn("先寫滿 6 條檢查，再告訴你是哪幾種", r.stdout)
            self.assertNotIn("邊界 24", r.stdout)
            self.assertIn("uv run check.py note", r.stdout)

        with self.subTest("1-9 第①②圈寫好、第③圈漏掉 24 的邊界"):
            write(work / "budget_light.py", (COURSE / "lessons/1-9/reference/budget_light.py").read_text(encoding="utf-8"))
            fill_answers(work / "trace.txt", ["過輕", "正常", "過重", "「肥胖」"])
            fill_answers(work / "ai_review.txt", ["不採用", "不採用", "採用", "不採用", "要查證", "採用"])
            base = (work / "checks_bmi.py").read_text(encoding="utf-8")
            asserts = ['assert bmi_level(22) == "正常"', 'assert bmi_level(25) == "過重"', 'assert bmi_level(30) == "肥胖"',
                       'assert bmi_level(18.5) == "正常"', 'assert bmi_level(23) == "正常"']
            write(work / "checks_bmi.py", base + "\n".join(asserts) + "\n")
            r = check(["1-9", "--predict", "18"], at(1, "10:30"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("✓ 官方測試  4／4", r.stdout)
            self.assertIn("✓ 對答  4／4", r.stdout)
            self.assertIn("✓ 第②圈  6／6", r.stdout)
            self.assertIn("你的檢查抓到 2 個壞版本，還有 1 個溜過去：\n    ・邊界 24", r.stdout)

        with self.subTest("特殊作答：已知會當掉真的拿正確版跑；需求有問題照規則"):
            extra = ['assert bmi_level("23") == "正常"  # 已知會當掉', "assert bmi_level(-5) == '錯誤'  # 需求有問題",
                     'assert bmi_level() == "過輕"  # 已知會當掉',
                     "assert bmi_level(25) == '過輕'  # 需求有問題", "assert bmi_level(25) == '過重'  # 已知會當掉"]
            write(work / "checks_bmi.py", base + "\n".join(asserts + extra) + "\n")
            r = check(["1-9", "--predict", "17", "--all"], at(1, "10:35"))
            self.assertIn("標了「已知會當掉」（bmi_level('23')：正確版跑這一行真的會當掉", r.stdout)
            self.assertIn("標了「需求有問題」（bmi_level(-5)", r.stdout)
            self.assertIn("標了「已知會當掉」（bmi_level()：正確版跑這一行真的會當掉（TypeError", r.stdout)
            self.assertIn("可是 bmi_level(25) 的需求講得很清楚", r.stdout)
            self.assertIn("可是正確版跑 bmi_level(25) 並不會當掉", r.stdout)
            self.assertIn("✓ 你的檢查在正確版上要全部成立", r.stdout)

        with self.subTest("寫錯的檢查：在正確版上就不成立"):
            write(work / "checks_bmi.py", base + "\n".join(asserts + ["assert bmi_level(24) == '正常'"]) + "\n")
            r = check(["1-9", "--predict", "15"], at(1, "10:37"))
            self.assertIn("在正確版上就不成立（正確版算出來是「過重」）", r.stdout)

        with self.subTest("1-9 全過（40 分鐘，不跳警訊），回顧題最多兩題"):
            final = asserts + ["assert bmi_level(24) == '過重'"] + extra[:2]
            write(work / "checks_bmi.py", base + "\n".join(final) + "\n")
            r = check(["1-9", "--predict", "21"], at(1, "10:40"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("全部 21 題都過了", r.stdout)
            self.assertIn("一共 40 分鐘", r.stdout)
            self.assertNotIn("這是警訊", r.stdout)
            self.assertIn("今天到期的回顧題（2 題）", r.stdout)
            self.assertIn("[0-4:r1]（複習 0-4）", r.stdout)
            self.assertIn("[0-4:r2]（複習 0-4）", r.stdout)
            self.assertNotIn("[0-5:", r.stdout)

        with self.subTest("start 不會蓋掉已經寫好的作業"):
            mine = (work / "budget_light.py").read_text(encoding="utf-8")
            r = check(["start", "1-9"], at(1, "10:45"))
            self.assertIn("這些已經有了，沒有蓋掉", r.stdout)
            self.assertEqual((work / "budget_light.py").read_text(encoding="utf-8"), mine)

        # ---------- 回顧題 ----------
        with self.subTest("同一天答對不算葉子；答錯給正確答案、換一題"):
            r = check(["review", "0-4:r1", "/Users/bear/code"], at(1, "11:00"))
            self.assertEqual(r.returncode, 0)
            self.assertIn("今天跟你通過 0-4 是同一天，先不算葉子", r.stdout)
            r = check(["review", "0-4:r2", "會"], at(1, "11:01"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("✗ 這題先算錯，下次會換一題再問你。", r.stdout)
            self.assertIn("正確答案：不會", r.stdout)
            r = check(["review"], at(1, "11:02"))
            self.assertIn("[0-4:r2]", r.stdout)  # 2 課前那一格：同一天答對以後換下一題
            self.assertIn("[0-4:r3]", r.stdout)  # 5 課前那一格：答錯之後換下一題
            self.assertNotIn("[0-4:r1]", r.stdout)

        with self.subTest("隔天只答回顧題：長葉子，也算一天練習"):
            r = check(["review", "0-4:r2", "不會"], at(2, "08:30"))
            self.assertEqual(r.returncode, 0)
            self.assertIn("技能樹長出一片葉子", r.stdout)
            r = check(["review", "0-4:r2", "不會"], at(2, "08:31"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("現在沒有到期", r.stdout)
            r = check(["review", "0-4:r3", "B. 先停下來"], at(2, "08:32"))
            self.assertIn("技能樹長出一片葉子", r.stdout)
            r = check(["review"], at(2, "08:33"))
            self.assertIn("[0-5:r1]", r.stdout)
            self.assertIn("[0-5:r2]", r.stdout)
            r = check(["status"], at(2, "08:34"))
            self.assertIn("練習天數：2 天", r.stdout)

        # ---------- Lv0 關卡 ----------
        work = ledger / "lessons" / "0-C"
        with self.subTest("lv0 開始前預測，4 分鐘全對跳警訊；保險箱、存檔點、重建計時"):
            r = check(["start", "lv0", "--predict", "10"], at(2, "09:00"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("開始前你猜會過 10／16 題", r.stdout)
            self.assertTrue((ledger / "lessons" / DECOY / "收據.txt").is_file())
            build_0_4_tree(work / "rebuild")
            fill_answers(work / "pwd.txt", ["/Users/bear/code/ledger", "/Users/bear/code/ledger/data/receipts",
                                            "/Users/bear/code/ledger", "~/code/ledger/notes", "/Users/bear/"])
            write(work / "main.py", (COURSE / "lessons/0-C/reference/main.py").read_text(encoding="utf-8"))
            shutil.copyfile(ledger / "main.py", ledger / "hello_backup.py")
            fill_answers(work / "ai_explain.txt", ["B"])
            script = (work / "make_v0.sh").read_text(encoding="utf-8")
            self.assertIn(f"rm -rf ../{DECOY}", script)
            self.assertNotIn("../0-4", script)
            write(work / "make_v0.sh", "\n".join(ln for ln in script.splitlines() if "rm -rf" not in ln) + "\n")
            # 模擬「bash make_v0.sh」跑過的結果（測試不依賴 bash，Windows 也一樣）
            (work / "v0" / "data").mkdir(parents=True)
            (work / "v0" / "notes").mkdir(parents=True)
            (work / "v0" / "notes" / "budget.txt").touch()
            shutil.copyfile(ledger / "main.py", work / "v0" / "main_backup.py")
            write(work / "checks.txt", f"v0/data/\nv0/notes/budget.txt\nv0/main_backup.py\n../{DECOY}/收據.txt\n../../main.py\n")

            # 存檔點還沒做、main.py 還是 Hello：第一關擋下來
            r = check(["lv0", "--predict", "14", "--all", "--no-review"], at(2, "09:02"))
            self.assertIn("第一關重建資料夾：照檔案時間算，大約花了不到 1 分鐘（標準是 10 分鐘內）。做到了！", r.stdout)
            self.assertIn("帳本還不是 git 存放庫", r.stdout)
            self.assertIn("cp lessons/0-C/main.py main.py", r.stdout)

            git(ledger, "init", "--quiet")
            git(ledger, "add", "-A")
            git(ledger, "commit", "--quiet", "-m", "第一個存檔點")
            shutil.copyfile(work / "main.py", ledger / "main.py")
            r = check(["lv0", "--predict", "14", "--all", "--no-review"], at(2, "09:03"))
            self.assertIn("帳本現在有 1 個存檔點，這一關要至少 2 個", r.stdout)
            git(ledger, "add", "main.py")
            git(ledger, "commit", "--quiet", "-m", "帳本 v0")

            r = check(["lv0", "--predict", "15"], at(2, "09:04"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("全部 16 題都過了", r.stdout)
            self.assertNotIn("第一關重建資料夾", r.stdout)  # 只在第一次重建成功時說一次
            self.assertIn("這是警訊", r.stdout)
            self.assertIn("關卡要關掉 AI 自己做", r.stdout)
            self.assertIn("從開始這課到這次全過，一共 4 分鐘", r.stdout)
            self.assertIn("關卡進度：第一關 ✓  第二關 ✓  第三關 ✓", r.stdout)
            self.assertIn("開始前你猜 10 題，做完猜 15 題，實際 16 題", r.stdout)
            self.assertIn("練習天數 2／3 天", r.stdout)

        with self.subTest("lv0 的危險指令沒刪：模擬抓得到"):
            write(work / "make_v0.sh", script)
            r = check(["lv0", "--predict", "14", "--no-review"], at(2, "09:30"))
            self.assertEqual(r.returncode, 1)
            self.assertIn(f"跑你的版本，../{DECOY}/ 會不見", r.stdout)
            write(work / "make_v0.sh", "\n".join(ln for ln in script.splitlines() if "rm -rf" not in ln) + "\n")

        with self.subTest("第三天：練滿 3 天，升級"):
            r = check(["lv0", "--predict", "16"], at(3, "20:00"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("這次是複習", r.stdout)
            self.assertIn("★ Lv0 新手村過關", r.stdout)

        # ---------- 其他行為 ----------
        with self.subTest("預測不合理"):
            r = check(["1-9", "--predict", "99"], at(3, "20:10"))
            self.assertEqual(r.returncode, 2)
            self.assertIn("預測要是 0 到", r.stdout)
            r = check(["1-9", "--predict", "½", "--no-review"], at(3, "20:10"))
            self.assertEqual(r.returncode, 2)
            self.assertIn("不是數字", r.stdout)
            self.assertNotIn("Traceback", r.stdout + r.stderr)

        with self.subTest("「19題」、破折號課號都收"):
            r = check(["1–9", "--predict", "19題", "--no-review"], at(3, "20:10"))
            self.assertIn("你猜 19 題", r.stdout)

        with self.subTest("沒給預測（非互動）照樣跑，不記校準"):
            r = check(["0-4", "--no-review"], at(3, "20:11"))
            self.assertIn("沒有收到你的預測", r.stdout)
            attempts = [json.loads(x) for x in (ledger / ".check" / "attempts.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertIsNone(attempts[-1]["predicted"])

        with self.subTest("環境變數給預測（測試用）"):
            env = make_env(home, at(3, "20:12"))
            env["PLUSFORM_PREDICT"] = "12"
            r = run_check(["0-4", "--no-review"], env)
            self.assertIn("你猜 12 題，實際過了 12 題：完全猜中", r.stdout)

        with self.subTest("note 和 status"):
            r = check(["note", "下次我會先看邊界再猜"], at(3, "20:15"))
            self.assertEqual(r.returncode, 0)
            r = check(["status"], at(3, "20:16"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            out = r.stdout
            for lid in ("0-4", "0-5", "0-C", "1-9"):
                self.assertRegex(out, rf"✓ {lid}\s")
            self.assertIn("已升級", out)
            self.assertIn("重建花了不到 1 分鐘", out)
            self.assertIn("練習天數：3 天", out)
            self.assertIn("技能樹的葉子：2 片", out)
            self.assertIn("太快全對的警訊：0-C", out)
            self.assertIn("校準曲線", out)
            self.assertRegex(out, r"最近 5 次平均差 \d+%")
            self.assertIn("下次我會先看邊界再猜", out)
            self.assertIn("看得懂進度條：[", out)
            # 關卡記下三關各自第一次全部通過的日期，以及第一次對答案時的兩次預測
            self.assertIn("第一關✓11/11 第二關✓11/11 第三關✓11/11", out)
            self.assertIn("0-C 關卡第一次對答案：開始前猜 10、做完猜 14、實際 ", out)

        with self.subTest("紀錄都在帳本的 .check，課程資料夾什麼都沒寫"):
            prog = json.loads((ledger / ".check" / "progress.json").read_text(encoding="utf-8"))
            for lid in ("0-4", "0-5", "0-C", "1-9"):
                self.assertTrue(prog["lessons"][lid]["first_pass"])
            self.assertEqual(prog["lessons"]["0-C"]["fast_warning_minutes"], 4.0)
            self.assertNotIn("fast_warning_minutes", prog["lessons"]["1-9"])
            self.assertTrue((ledger / ".check" / "reviews.jsonl").is_file())
            self.assertEqual(snapshot(COURSE), before)
            self.assertEqual(list(COURSE.rglob("__pycache__")), [])


@unittest.skipIf(UV is None, "需要 uv")
class UvRunScript(unittest.TestCase):
    def test_uv_run_check_help(self):
        home = fresh_dir("uvrun_home")
        r = subprocess.run([UV, "run", "--quiet", "check.py", "--help"], cwd=COURSE, env=make_env(home),
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("uv run check.py setup", r.stdout)
        r = subprocess.run([UV, "run", "--quiet", "concept_map.py", "--upto", "1-27"], cwd=COURSE, env=make_env(home),
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("100%", r.stdout)


if __name__ == "__main__":
    unittest.main()
