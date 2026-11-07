# /// script
# requires-python = ">=3.13"
# ///
"""老師端：驗證一課的題目本身沒有問題。壞版本收進題庫之前一定要跑。

用法（在課程資料夾裡打）：
    uv run tools/validate_lesson.py              驗證全部做好的課
    uv run tools/validate_lesson.py 1-9 0-4      只驗證這幾課
    uv run tools/validate_lesson.py --no-env     跳過需要臨時帳本的檢查（0-5 的 doctor.py）
    uv run tools/validate_lesson.py --root 路徑  驗證另一份課程資料夾（測試用）

驗證規則（照總企劃第七節，加上審查後補的幾條）：
  1. 每個壞版本至少讓一個「參考測試」變紅。參考測試＝同一個檔案的官方測試，
     加上 answers/ 裡老師寫的標準檢查（teacher_file）。
  2. 壞版本要「藏得住」：不能一載入就當掉、不能有語法錯誤、不能每一條參考測試都紅
     （老師的標準檢查至少要有一條在它上面成立）。不然學員隨便寫一條都抓得到。
  3. 正確版通過全部官方測試，也通過老師的標準檢查（全綠）。
  4. 起點檔（start/）沒問題：裡面的範例檢查在正確版上要成立；起點程式不能一開始就通過全部官方測試；
     起點腳本不能跟安全版一模一樣。
  5. 正確版、壞版本、起點檔、參考答案只用了 CONCEPTS.md 列的概念或終端機指令（用 ast 粗略檢查）；
     CONCEPTS.md 列的每個概念，教的課不能比這課晚，除非標成「例外」並寫理由（會列出來）。
  6. 檔案齊全：README 的六段、lesson.json、tests/checks.json、start/、review/、CONCEPTS.md，
     每個 chaff 有 3 個壞版本；answers 的題數跟 start/ 作答檔的「答：」行數一樣；
     回顧題格式正確；「已知會當掉」的例子真的會讓正確版當掉；腳本只用假終端機模擬得了的寫法。

只用 Python 標準庫。臨時帳本建在系統的暫存資料夾（TMPDIR），用完就刪；不寫課程資料夾。
任何一課出了意外，都只算那一課有問題，不會整支當掉。
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import ast  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import traceback  # noqa: E402
from pathlib import Path  # noqa: E402

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import concept_map  # noqa: E402
from engine import grader, vshell  # noqa: E402

README_SECTIONS = ["題目", "提示", "開始前要打的指令", "成品示範", "怎麼測", "怎麼交"]
MUTANTS_PER_LESSON = 3


def parse_concepts_md(path: Path) -> tuple[set[str], set[str], list[str], dict[str, str]]:
    """回傳（可以用的概念, 可以用的指令, 對不到的名字, {例外的概念: 理由}）。"""
    concepts: set[str] = set()
    commands: set[str] = set()
    unknown: list[str] = []
    exceptions: dict[str, str] = {}
    section = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("#"):
            section = "cmd" if "指令" in line else "concept" if "概念" in line else None
            continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if not m or section is None:
            continue
        item = m.group(1)
        name = re.split(r"[（(：:]", item)[0].strip().strip("`").strip()
        if section == "cmd":
            commands.add(name)
            continue
        key = concept_map.name_to_key(name)
        if not key:
            unknown.append(name)
            continue
        concepts.add(key)
        ex = re.search(r"例外[：:]\s*(.*?)[）)]?\s*$", item)
        if ex:
            exceptions[key] = ex.group(1).strip() or "（沒寫理由）"
    return concepts, commands, unknown, exceptions


def shell_commands(text: str) -> set[str]:
    out: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        for _joiner, words in vshell._split_commands(line):
            if words:
                out.add(words[0])
    return out


def strip_comments(text: str) -> str:
    return "\n".join(ln for ln in (x.strip() for x in text.splitlines()) if ln and not ln.startswith("#"))


def make_temp_ledger() -> tuple[Path, Path]:
    uv = grader.find_uv()
    if not uv:
        raise RuntimeError("找不到 uv")
    top = Path(tempfile.mkdtemp(prefix="plusform-validate-"))
    ledger = top / "ledger"
    ledger.mkdir()
    env = grader.child_env()
    subprocess.run([uv, "init", "--no-package", "--vcs", "none", "--name", "ledger", "--quiet"],
                   cwd=ledger, check=True, env=env, capture_output=True)
    subprocess.run([uv, "python", "pin", "3.13", "--quiet"], cwd=ledger, check=True, env=env, capture_output=True)
    return top, ledger


class Report:
    def __init__(self, lid: str):
        self.lid = lid
        self.problems: list[str] = []
        self.oks: list[str] = []
        self.skips: list[str] = []
        self.notes: list[str] = []

    def ok(self, text: str) -> None:
        self.oks.append(text)

    def bad(self, text: str) -> None:
        self.problems.append(text)

    def skip(self, text: str) -> None:
        self.skips.append(text)

    def note(self, text: str) -> None:
        self.notes.append(text)

    def print(self) -> None:
        print(f"━━ {self.lid} ━━")
        for t in self.oks:
            print(f"  ✓ {t}")
        for t in self.notes:
            print(f"  ※ {t}")
        for t in self.skips:
            print(f"  － {t}")
        for t in self.problems:
            print(f"  ✗ {t}")
        print(f"  結果：{'沒問題' if not self.problems else f'有 {len(self.problems)} 個問題'}")


def lesson_index(lid: str, order: list[str]) -> int:
    return order.index(lid) if lid in order else len(order)


def check_concepts(rep: Report, lesson: grader.Lesson, order: list[str]) -> None:
    d = lesson.dir
    concepts_md = d / "CONCEPTS.md"
    if not concepts_md.is_file():
        return
    allowed, commands, unknown, exceptions = parse_concepts_md(concepts_md)
    for name in unknown:
        rep.bad(f"CONCEPTS.md 裡的「{name}」對不到 concept_map.py 的概念名稱")
    here = lesson_index(lesson.id, order)
    for key in sorted(allowed, key=list(concept_map.CONCEPTS).index):
        label, teach = concept_map.CONCEPTS[key]
        later = teach is None or lesson_index(teach, order) > here
        if later and key not in exceptions:
            rep.bad(f"CONCEPTS.md 的「{label}」要到 {teach or '（課表沒有）'} 才教，比這課（{lesson.id}）晚。"
                    "真的要用，就標成「例外：理由」")
        elif later:
            rep.note(f"例外：「{label}」（{teach} 才教）— {exceptions[key]}")
        elif key in exceptions:
            rep.note(f"「{label}」標了例外，可是 {teach} 就教過了，不用標")

    scanned = 0
    bad_before = len(rep.problems)
    for folder in ("reference", "mutants", "start", "answers"):
        files = sorted((d / folder).glob("*")) if (d / folder).is_dir() else []
        for f in files:
            if f.suffix == ".py":
                try:
                    used = concept_map.concepts_in_source(f.read_text(encoding="utf-8"))
                except SyntaxError as exc:
                    if folder == "start":  # 起點檔可以故意壞掉（例如 0-C 要學員修好的 main.py）
                        rep.note(f"起點檔 start/{f.name} 第 {exc.lineno} 行故意有語法錯誤，這個檔不做概念檢查")
                    else:
                        rep.bad(f"{folder}/{f.name} 第 {exc.lineno} 行有語法錯誤（{exc.msg}）")
                    continue
                extra = used - allowed
                if extra:
                    names = "、".join(concept_map.label(k) for k in sorted(extra))
                    rep.bad(f"{folder}/{f.name} 用到 CONCEPTS.md 沒列的概念：{names}")
                scanned += 1
            elif f.suffix == ".sh":
                extra = shell_commands(f.read_text(encoding="utf-8")) - commands
                if extra:
                    rep.bad(f"{folder}/{f.name} 用到 CONCEPTS.md 沒列的指令：{'、'.join(sorted(extra))}")
                scanned += 1
    if scanned and len(rep.problems) == bad_before:
        rep.ok(f"正確版、壞版本、起點檔、參考答案（{scanned} 個檔）只用了 CONCEPTS.md 列的概念")


def check_files(rep: Report, lesson: grader.Lesson) -> None:
    d = lesson.dir
    missing = [f for f in ("README.md", "lesson.json", "tests/checks.json", "CONCEPTS.md", "review/questions.json")
               if not (d / f).is_file()]
    if not (d / "start").is_dir() or not any((d / "start").iterdir()):
        missing.append("start/（起點檔）")
    for f in missing:
        rep.bad(f"少了 {f}")
    if (d / "README.md").is_file():
        text = (d / "README.md").read_text(encoding="utf-8")
        heads = [ln for ln in text.splitlines() if ln.startswith("#")]
        lacking = [s for s in README_SECTIONS if not any(s in h for h in heads)]
        if lacking:
            rep.bad("README 少了這幾段：" + "、".join(lacking))
    if not missing:
        rep.ok("檔案齊全，README 有固定的六段")

    try:
        questions = lesson.review_questions()
        ids = [q.get("id") for q in questions]
        broken = [q for q in questions if not q.get("id") or not q.get("q") or not q.get("accept")]
        if not questions:
            rep.bad("review/questions.json 沒有題目")
        elif broken or len(set(ids)) != len(ids):
            rep.bad("回顧題格式不對（每題要有不重複的 id、q、accept）")
        else:
            rep.ok(f"回顧題 {len(questions)} 題格式正確")
    except (ValueError, OSError) as exc:
        rep.bad(f"review/questions.json 讀不懂：{exc}")


def run_script_ok(rep: Report, label: str, text: str, sc: dict) -> vshell.VResult:
    res = vshell.run(text, sc["home"], sc["cwd"], sc.get("start", []))
    odd = [msg for _ln, msg in res.errors if msg.startswith("有模擬器")]
    if odd:
        rep.bad(f"{label} 有假終端機模擬不了的寫法：{odd[0]}")
    return res


def validate_lesson(lid: str, root: Path, use_env: bool, temp: dict) -> Report:
    rep = Report(lid)
    try:
        lesson = grader.load_lesson(lid, root)
    except grader.LessonNotFound:
        rep.bad(f"找不到 lessons/{lid}/lesson.json")
        return rep
    d = lesson.dir
    order = grader.course_order(grader.course_info(root))

    check_files(rep, lesson)
    local = grader.Env(None, local=True)

    for spec in lesson.checks:
        if spec["type"] == "answers":
            key = json.loads((d / spec["key"]).read_text(encoding="utf-8"))
            template = d / "start" / Path(spec["file"]).name
            if not template.is_file():
                rep.bad(f"{spec['file']} 在 start/ 裡沒有作答檔")
                continue
            n = len(grader.read_answer_lines(template))
            if n != len(key["questions"]):
                rep.bad(f"{template.name} 有 {n} 個「答：」，可是 {spec['key']} 有 {len(key['questions'])} 題")
            else:
                rep.ok(f"{template.name} 的題數跟 {spec['key']} 一樣（{n} 題）")
            if key.get("choices"):
                outside = [a for q in key["questions"] for a in q["accept"] if a.upper() not in {c.upper() for c in key["choices"]}]
                if outside:
                    rep.bad(f"{spec['key']} 的答案 {outside[0]} 不在選項裡")
        elif spec["type"] == "tree":
            if not (d / spec["spec"]).is_file():
                rep.bad(f"找不到 {spec['spec']}")
        elif spec["type"] == "script_match":
            sc = json.loads((d / spec["scenario"]).read_text(encoding="utf-8"))
            ref_text = (d / spec["reference"]).read_text(encoding="utf-8")
            res = run_script_ok(rep, spec["reference"], ref_text, sc)
            if res.errors:
                rep.bad(f"{spec['reference']} 在假的資料夾裡會出錯：{res.errors[0][1]}")
            else:
                rep.ok(f"{spec['reference']} 在假的資料夾裡跑得完")
            start = d / "start" / Path(spec["student_file"]).name
            if start.is_file():
                mine = run_script_ok(rep, f"start/{start.name}", start.read_text(encoding="utf-8"), sc)
                extra, lost = vshell.diff(mine, res, sc["cwd"])
                if not (extra or lost or mine.errors):
                    rep.bad(f"起點檔 start/{start.name} 跟安全版跑起來一樣：學員什麼都不用改就過了")
                else:
                    rep.ok(f"起點檔 start/{start.name} 跟安全版不一樣（學員要自己找出問題）")

    check_concepts(rep, lesson, order)

    # ---- 3. 正確版通過官方測試；4. 起點程式不能一開始就全過 ----
    official = [s for s in lesson.checks if s["type"] in ("call", "run")]
    covered = 0
    for spec in official:
        ref = d / "reference" / Path(spec["file"]).name
        if not ref.is_file():
            continue
        out = grader.evaluate(lesson, None, env=local, overrides={spec["file"]: ref}, only=[spec])
        for r in out.results:
            if not r.ok:
                rep.bad(f"正確版 reference/{ref.name} 沒通過官方測試「{r.desc}」：{r.detail}")
        covered += 1
    if covered:
        rep.ok(f"正確版通過 {covered} 項官方測試")
    by_file: dict[str, list[dict]] = {}
    for spec in official:
        by_file.setdefault(spec["file"], []).append(spec)
    for rel, specs in by_file.items():
        start = d / "start" / Path(rel).name
        if not start.is_file():
            continue
        out = grader.evaluate(lesson, None, env=local, overrides={rel: start}, only=specs)
        if out.results and all(r.ok for r in out.results):
            rep.bad(f"起點檔 start/{start.name} 一開始就通過全部 {len(specs)} 項官方測試：學員什麼都不用做")
        else:
            rep.ok(f"起點檔 start/{start.name} 還沒通過官方測試（學員要自己寫）")

    # ---- 1、2. 壞版本 ----
    for spec in lesson.checks:
        if spec["type"] != "chaff":
            continue
        info = json.loads((d / spec["mutants"]).read_text(encoding="utf-8"))
        mutants = info["mutants"]
        mdir = (d / spec["mutants"]).parent
        ref_path = d / spec["reference"]
        if len(mutants) != MUTANTS_PER_LESSON:
            rep.bad(f"{spec['mutants']} 有 {len(mutants)} 個壞版本，規定是 {MUTANTS_PER_LESSON} 個")
        sc = json.loads((d / spec["scenario"]).read_text(encoding="utf-8")) if spec.get("scenario") else None
        usable = {}
        for i, m in enumerate(mutants, start=1):
            mp = mdir / m["file"]
            if not mp.is_file():
                rep.bad(f"找不到壞版本 {m['file']}")
                continue
            text = mp.read_text(encoding="utf-8")
            if strip_comments(text) == strip_comments(ref_path.read_text(encoding="utf-8")):
                rep.bad(f"壞版本 {m['file']} 跟正確版一模一樣")
            if mp.suffix == ".py":
                try:
                    ast.parse(text)
                except SyntaxError as exc:
                    rep.bad(f"壞版本 {m['file']} 第 {exc.lineno} 行有語法錯誤：一載入就壞，任何檢查都抓得到它")
                    continue
                if spec["mode"] == "assert":
                    reply = local.runner({"op": "load", "file": str(mp), "module": spec["module"]})
                    if reply.get("load_error"):
                        err = reply["load_error"]
                        rep.bad(f"壞版本 {m['file']} 一載入就當掉（{err.get('msg')}）：任何檢查都抓得到它")
                        continue
            elif mp.suffix == ".sh" and sc:
                run_script_ok(rep, f"壞版本 {m['file']}", text, sc)
            usable[i] = mp
        if sc and ref_path.suffix == ".sh":
            run_script_ok(rep, spec["reference"], ref_path.read_text(encoding="utf-8"), sc)
        if not spec.get("teacher_file"):
            rep.bad(f"{spec['id']} 沒有 teacher_file（老師的標準檢查）")
            continue

        env = local
        if spec.get("needs_ledger"):
            if not use_env:
                rep.skip(f"{spec['id']}（{spec['mode']}）要臨時帳本，這次用 --no-env 跳過")
                continue
            if "ledger" not in temp:
                try:
                    temp["top"], temp["ledger"] = make_temp_ledger()
                except (RuntimeError, subprocess.CalledProcessError) as exc:
                    rep.bad(f"建不起臨時帳本，沒辦法驗證 {spec['id']}：{exc}")
                    continue
            env = grader.Env(temp["ledger"])

        teacher = d / spec["teacher_file"]
        ledger = temp.get("ledger") if spec.get("needs_ledger") else None
        ctx, checkers = grader.build(lesson, ledger, env=env, overrides={spec["student_file"]: teacher}, only=[spec])
        ch = checkers[0]
        parsed = ch.parse()
        if parsed.problem:
            rep.bad(f"老師的標準檢查 {spec['teacher_file']} 讀不懂：{parsed.problem}")
            continue
        if len(parsed.checks) < ch.min:
            rep.bad(f"老師的標準檢查 {spec['teacher_file']} 只有 {len(parsed.checks)} 條，這課要至少 {ch.min} 條")
        st, _marks = ch.statuses(parsed.checks, parsed.marks)
        ref_rows = st["reference"]
        bad_ref = [(c, s) for c, s in zip(parsed.checks, ref_rows) if s.get("status") != "pass"]
        if bad_ref:
            rep.bad(f"正確版沒通過老師的標準檢查：{ch.describe_ref_failure(*bad_ref[0])}")
        else:
            rep.ok(f"正確版通過老師的標準檢查（{spec['teacher_file']}）")

        target = spec.get("target")
        target_tests = [s for s in official if target and s["file"] == target]
        for i, m in enumerate(mutants, start=1):
            if i not in usable:
                continue
            rows = st[f"m{i}"]
            holds = sum(1 for r in rows if r.get("status") == "pass")
            if rows and all(r.get("status") == "error" for r in rows):
                rep.bad(f"壞版本 {m['file']} 一跑就當掉（{rows[0].get('error')}）：任何檢查都抓得到它")
                continue
            red = []
            if any(ref.get("status") == "pass" and r.get("status") != "pass" for ref, r in zip(ref_rows, rows)):
                red.append("老師的標準檢查")
            n_red = 0
            if target_tests:
                res = grader.evaluate(lesson, None, env=local, overrides={target: usable[i]}, only=target_tests)
                n_red = sum(1 for r in res.results if not r.ok)
                if n_red:
                    red.append(f"{n_red} 項官方測試")
            if not red:
                rep.bad(f"壞版本 {m['file']} 沒有讓任何參考測試變紅，學員不可能抓到它")
            elif holds == 0:
                rep.bad(f"壞版本 {m['file']} 在老師的標準檢查上一條都不成立：太明顯了，學員隨便寫一條都抓得到它")
            elif target_tests and n_red == len(target_tests):
                rep.bad(f"壞版本 {m['file']} 讓全部 {n_red} 項官方測試都變紅：太明顯了，藏不住")
            else:
                rep.ok(f"壞版本 {m['file']} 會讓 {'、'.join(red)} 變紅，"
                       f"老師的檢查有 {holds} 條在它上面成立（藏得住）（{m.get('what', m['hint'])}）")

        # ---- 4. 起點檔裡的範例檢查，在正確版上要成立 ----
        start = d / "start" / Path(spec["student_file"]).name
        if start.is_file():
            _c2, chk2 = grader.build(lesson, ledger, env=env, overrides={spec["student_file"]: start}, only=[spec])
            p2 = chk2[0].parse()
            if p2.problem:
                rep.bad(f"起點檔 start/{start.name} 讀不懂：{p2.problem}")
            elif p2.checks:
                st2, _ = chk2[0].statuses(p2.checks, p2.marks)
                wrong = [(c, s) for c, s in zip(p2.checks, st2["reference"]) if s.get("status") != "pass"]
                if wrong:
                    rep.bad(f"起點檔 start/{start.name} 的範例檢查在正確版上不成立：{chk2[0].describe_ref_failure(*wrong[0])}")
                else:
                    rep.ok(f"起點檔 start/{start.name} 的 {len(p2.checks)} 條範例檢查在正確版上都成立")

        if spec.get("special"):
            key = json.loads((d / spec["special"]).read_text(encoding="utf-8"))
            for rule in key.get("rules", []):
                for ex in rule.get("examples", []):
                    args = [ast.literal_eval(ex)]
                    if not grader._rule_matches(rule, args):
                        rep.bad(f"special 的例子 {ex} 不符合它自己的規則（{rule['kind']}）")
                        continue
                    if rule["kind"] == "已知會當掉":
                        reply = local.runner({"op": "call", "file": str(ref_path), "module": spec.get("module", "impl"),
                                              "func": key["func"], "cases": [{"args": args, "expect": None}]})
                        cases = reply.get("cases") or [{}]
                        if "error" not in cases[0]:
                            rep.bad(f"「已知會當掉」的例子 {key['func']}({ex}) 在正確版上並沒有當掉")
                        else:
                            rep.ok(f"「已知會當掉」的例子 {key['func']}({ex}) 在正確版上確實會當掉")
    return rep


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(description="驗證課程題目（老師端）")
    p.add_argument("lessons", nargs="*", help="課號，不寫就驗證全部做好的課")
    p.add_argument("--no-env", action="store_true", help="跳過需要臨時帳本的檢查")
    p.add_argument("--root", default=str(ENGINE_ROOT), help="課程資料夾（預設是這一份）")
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    course = grader.course_info(root)
    ids = [grader.normalize_id(x, course) for x in args.lessons] or grader.available_lessons(root)
    temp: dict = {}
    failed = 0
    try:
        for lid in ids:
            try:
                rep = validate_lesson(lid, root, not args.no_env, temp)
            except Exception as exc:  # noqa: BLE001 - 一課出意外，只算那一課有問題
                rep = Report(lid)
                where = traceback.extract_tb(exc.__traceback__)[-1]
                rep.bad(f"驗證時出了意外：{type(exc).__name__}: {exc}（{Path(where.filename).name} 第 {where.lineno} 行）")
            rep.print()
            failed += bool(rep.problems)
    finally:
        if "top" in temp:
            shutil.rmtree(temp["top"], ignore_errors=True)
    print()
    print(f"驗證了 {len(ids)} 課：{'全部沒問題' if not failed else f'{failed} 課有問題'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
