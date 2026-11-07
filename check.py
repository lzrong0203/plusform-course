# /// script
# requires-python = ">=3.13"
# ///
"""新時代程式課的檢查程式。

在課程資料夾裡打：
    uv run check.py setup ~/code/ledger   記住你的帳本在哪裡（只要做一次）
    uv run check.py start 1-9             把這課的起點檔複製到帳本
    uv run check.py 1-9                   檢查這一課
    uv run check.py status                看進度、到期的回顧題、你猜得準不準
    uv run check.py review                作答今天到期的回顧題

五個固定行為：
  1. 跑檢查之前，先問「你猜會過幾題」，記下來畫校準曲線
  2. 一開始只顯示第一個沒過的（加 --all 看全部）
  3. 記下第一次跑和這次跑的時間差，太快全對會跳出警訊
  4. 提醒今天到期的回顧題（2 課前、5 課前各一題；跟上課不同天答對才算葉子）
  5. 接受兩種特殊作答：行尾標「# 已知會當掉」或「# 需求有問題」，標了就改成對答案

只用 Python 標準庫，絕不呼叫任何 AI 或網路服務。
課程資料夾裡什麼都不寫：進度都記在你的帳本 <帳本>/.check/ 裡。
"""

from __future__ import annotations

import sys

# 這一段要寫得連舊版 Python（例如 Mac 內建的 3.9）都看得懂，才能好好說明，而不是噴一堆錯誤
if sys.version_info < (3, 13):
    print("check.py 要用 Python 3.13 跑，你現在用的是 Python %d.%d。" % sys.version_info[:2])
    print("請在課程資料夾裡打：uv run check.py ……（前面是 uv run，不要用 python3 check.py）")
    print("例如：uv run check.py status")
    sys.exit(2)

sys.dont_write_bytecode = True  # 課程資料夾裡什麼都不寫（連 __pycache__ 也不要）

import os  # noqa: E402
import re  # noqa: E402
import shlex  # noqa: E402
import shutil  # noqa: E402
import unicodedata  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import concept_map  # noqa: E402
from engine import grader, state  # noqa: E402

PREDICT_ENV = "PLUSFORM_PREDICT"  # 測試用：不用一題一題問
BIG_GAP = 30  # 猜的跟實際差超過 30 個百分點，就請你寫一句「下次我會怎麼估」
SLOTS = (2, 5)  # 回顧題：2 課前、5 課前

HELP = """\
用法（在課程資料夾 plusform-course 裡打）：
  uv run check.py setup ~/code/ledger   記住你的帳本在哪裡（只要做一次）
  uv run check.py start 1-9             把這課的起點檔複製到帳本（已經有的檔案不會蓋掉）
  uv run check.py 1-9                   檢查這一課（課號像 0-4、0-5、1-9；Lv0 關卡打 lv0）
  uv run check.py status                看進度、到期的回顧題、你猜得準不準、看得懂進度條
  uv run check.py review                作答今天到期的回顧題
  uv run check.py note 一句話           寫下「下次我會怎麼估」

選項：
  --predict 數字   直接告訴它「你猜會過幾題」，不用等它問
  --all            一次看全部沒過的題目（平常只顯示第一個）
  --no-review      這次先不提醒回顧題

在別的資料夾也可以用完整路徑：uv run ~/code/plusform-course/check.py 1-9
"""


# ====================================================================
# 小工具
# ====================================================================

def setup_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def interactive() -> bool:
    try:
        if sys.stdin.isatty():
            return True
    except (AttributeError, ValueError):
        return False
    # Windows 的 Git Bash（mintty）有時候不會說自己是終端機，照樣一題一題問（要在 Windows 實機確認）
    if os.name == "nt" and (os.environ.get("MSYSTEM") or os.environ.get("TERM_PROGRAM") == "mintty"):
        return True
    return False


def ask(prompt: str) -> str | None:
    try:
        return input(prompt)
    except EOFError:
        return None


def mmdd(iso: str) -> str:
    t = state.parse_time(iso)
    return f"{t.month}/{t.day}"


def minutes_between(a: str, b: str) -> float:
    return (state.parse_time(b) - state.parse_time(a)).total_seconds() / 60


def fmt_minutes(m: float) -> str:
    if m < 1:
        return "不到 1 分鐘"
    if m < 90:
        return f"{round(m)} 分鐘"
    hours = m / 60
    if hours < 48:
        return f"{hours:.1f} 小時"
    return f"{hours / 24:.1f} 天"


def parse_args(argv: list[str]) -> tuple[list[str], dict]:
    opts = {"predict": None, "all": False, "no_review": False}
    pos: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--predict", "-p"):
            opts["predict"] = argv[i + 1] if i + 1 < len(argv) else ""
            i += 2
            continue
        if a.startswith("--predict="):
            opts["predict"] = a.split("=", 1)[1]
        elif a == "--all":
            opts["all"] = True
        elif a == "--no-review":
            opts["no_review"] = True
        elif a in ("-h", "--help"):
            pos = ["help"]
        else:
            pos.append(a)
        i += 1
    return pos, opts


def get_ledger() -> Path | None:
    cfg = state.load_config()
    if not cfg or not cfg.get("ledger"):
        print("還不知道你的帳本在哪裡。先打：")
        print("  uv run check.py setup ~/code/ledger")
        return None
    ledger = Path(cfg["ledger"])
    if not ledger.is_dir():
        print(f"設定裡記的帳本資料夾不見了：{ledger}")
        print("如果你搬了位置，重新打一次：uv run check.py setup <新的位置>")
        return None
    return ledger


def course() -> dict:
    return grader.course_info(ROOT)


def find_lesson(raw: str) -> grader.Lesson | None:
    info = course()
    lid = grader.normalize_id(raw, info)
    try:
        return grader.load_lesson(lid, ROOT)
    except grader.LessonNotFound:
        titles = grader.course_titles(info)
        ready = "、".join(grader.available_lessons(ROOT))
        if lid in titles:
            print(f"{lid}「{titles[lid]}」還沒做好。目前做好的課：{ready}")
        else:
            print(f"沒有「{raw}」這一課。課號長得像 0-5、1-9；Lv0 關卡打 lv0。")
            print(f"目前做好的課：{ready}")
        return None


# ====================================================================
# setup
# ====================================================================

SAFE_NAME = re.compile(r"[A-Za-z0-9._-]+")


def cmd_setup(args: list[str]) -> int:
    if not args:
        print("要告訴我帳本在哪裡，例如：uv run check.py setup ~/code/ledger")
        return 2
    raw = args[0]
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if not path.exists():
        print(f"找不到這個資料夾：{path}")
        print(f"先把它建起來：mkdir -p {shlex.quote(str(path))}")
        print("（也檢查一下有沒有打錯字。）")
        return 1
    if not path.is_dir():
        print(f"{path} 是一個檔案，不是資料夾。帳本要是一個資料夾。")
        return 1
    if path == ROOT or ROOT in path.parents:
        print("帳本不能放在課程資料夾裡面。課程資料夾之後會整包更新，放在裡面會被蓋掉。")
        print("建議放在：~/code/ledger")
        return 1
    if path == Path.home().resolve() or path.parent == path:
        print("帳本不能直接用家目錄（或整顆硬碟）。請另外建一個資料夾，建議放在：~/code/ledger")
        return 1
    old = state.ledger_from_config()
    records = state.Records(path)
    records.ensure()
    t = state.now()
    cfg_path = state.save_config({"ledger": str(path), "set_at": t.isoformat(timespec="seconds"), "course": str(ROOT)})
    print(f"記好了！你的帳本在：{path}")
    if old and old != path:
        print(f"（原本記的是 {old}，已經換成新的。舊的進度還留在那邊的 .check 資料夾裡。）")
    print(f"你的進度會記在：{records.dir}")
    print("課程資料夾裡什麼都不寫，所以更新課程也不會蓋掉你的進度。")
    print(f"這個設定存在：{cfg_path}")
    if path in ROOT.parents:
        print()
        print("⚠ 課程資料夾放在帳本裡面了（常見原因：下載後解壓縮到帳本裡）。")
        print("  建議把它搬出來，放在 ~/code/plusform-course，跟帳本並排。")
    print()
    if (path / "pyproject.toml").is_file():
        print("下一步：uv run check.py 0-5")
    else:
        if not SAFE_NAME.fullmatch(path.name):
            print(f"⚠ 帳本資料夾的名字「{path.name}」有中文、空白或符號，等一下 uv init 會說它不是合法的專案名稱。")
            print("  可以改用英文名字（例如 ledger），或在 uv init 後面加 --name ledger。")
        print("下一步：到帳本資料夾裡打 uv init --no-package --vcs none --python 3.13 和 uv python pin 3.13，")
        print("        再回到這裡打 uv run check.py 0-5")
    return 0


# ====================================================================
# start：把起點檔複製到帳本
# ====================================================================

def copy_start_file(src: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix == ".sh":
        # 腳本一律用 LF 換行：Windows 的 CRLF 會讓 bash 建出名字怪怪的資料夾
        target.write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))
    else:
        shutil.copyfile(src, target)


def cmd_start(args: list[str], opts: dict) -> int:
    if not args:
        print("要告訴我是哪一課，例如：uv run check.py start 1-9")
        return 2
    lesson = find_lesson(args[0])
    if lesson is None:
        return 1
    ledger = get_ledger()
    if ledger is None:
        return 1
    copied, kept = [], []
    pairs = [(lesson.dir / "start", ledger / "lessons" / lesson.id),
             (lesson.dir / "start_outside", ledger / "lessons")]
    for src, dest in pairs:
        if not src.is_dir():
            continue
        for path in sorted(src.rglob("*")):
            if path.is_dir() or path.name.startswith("."):
                continue
            target = dest / path.relative_to(src)
            rel = target.relative_to(ledger).as_posix()
            if target.exists():
                kept.append(rel)
                continue
            copy_start_file(path, target)
            copied.append(rel)
    print(f"━━ {lesson.id}  {lesson.title} ━━")
    if copied:
        print("複製到你的帳本：")
        for rel in copied:
            print(f"  + {rel}")
    if kept:
        print("這些已經有了，沒有蓋掉（想重來就先自己刪掉）：")
        for rel in kept:
            print(f"  = {rel}")
    if not copied and not kept:
        print("這課沒有起點檔，照 README 做就好。")

    records = state.Records(ledger)
    prog = records.progress()
    info = prog["lessons"].setdefault(lesson.id, {})
    t = state.now().isoformat(timespec="seconds")
    info.setdefault("start", t)
    if lesson.meta.get("gate") and info.get("pre_prediction") is None:
        total = len(grader.plan(lesson, ledger))
        print()
        print("關卡開始前，先寫下預測分數。")
        guess = get_prediction(total, opts, quiet_if_missing=True)
        if guess is not None:
            info["pre_prediction"] = guess
            print(f"記下來了：開始前你猜會過 {guess}／{total} 題。做完再猜一次，看看準不準。")
    records.save_progress(prog)
    after = lesson.meta.get("after_start")
    if after:
        print()
        print(after.replace("{ledger}", shlex.quote(str(ledger))))
    return 0


# ====================================================================
# 行為 1：先猜會過幾題
# ====================================================================

class BadPrediction(Exception):
    pass


def parse_prediction(raw: str, total: int) -> int:
    text = unicodedata.normalize("NFKC", raw).strip().removesuffix("題").strip()
    if not text.isdecimal():
        raise BadPrediction(f"「{raw}」不是數字。預測要是 0 到 {total} 的整數。")
    value = int(text)
    if not 0 <= value <= total:
        raise BadPrediction(f"這次一共只有 {total} 題，預測要是 0 到 {total} 的整數。")
    return value


def get_prediction(total: int, opts: dict, quiet_if_missing: bool = False) -> int | None:
    raw = opts.get("predict")
    if raw is None:
        raw = os.environ.get(PREDICT_ENV)
    if raw is not None:
        return parse_prediction(raw, total)
    if interactive():
        while True:
            ans = ask(f"這次一共要檢查 {total} 題。先猜猜看：你覺得會過幾題？（0–{total}）：")
            if ans is None:
                return None
            try:
                return parse_prediction(ans, total)
            except BadPrediction as exc:
                print(f"  {exc}")
    if not quiet_if_missing:
        print("（沒有收到你的預測，這次不記進校準曲線。下次可以在最後加上 --predict 數字）")
    return None


# ====================================================================
# 檢查一課
# ====================================================================

def show_outcome(outcome: grader.Outcome, show_all: bool, stages: list[str] | None) -> None:
    results = outcome.results
    print(f"結果：過了 {outcome.passed}／{outcome.total} 題")
    keys = stages if stages else list(dict.fromkeys(r.group for r in results))
    for key in keys:
        rows = [r for r in results if (r.stage if stages else r.group) == key]
        if not rows:
            continue
        ok = sum(1 for r in rows if r.ok)
        flag = "✓" if ok == len(rows) else "✗"
        print(f"  {flag} {key}  {ok}／{len(rows)}")
    for line in outcome.summaries:
        print(f"  {line}")

    failed = [r for r in results if not r.ok]
    for r in results:
        if r.ok and r.note and r.special:
            print(f"  ✓ {r.desc}：{r.note}")
    if show_all:
        print()
        for r in results:
            if r.ok:
                print(f"✓ {r.desc}" + (f"（{r.note}）" if r.note else ""))
            else:
                print(f"✗ {r.desc}")
                print(f"  {r.detail}")
        return
    if failed:
        first = failed[0]
        print()
        print(f"✗ 第一個沒過的：{first.desc}")
        print(f"  {first.detail}")
        if len(failed) > 1:
            print(f"（還有 {len(failed) - 1} 題沒過。先修這一題再跑一次；想一次看全部，加 --all）")


def calibration_line(predicted: int, passed: int, total: int) -> tuple[str, float]:
    gap = predicted - passed
    pct = gap * 100 / total if total else 0.0
    if gap == 0:
        text = f"你猜 {predicted} 題，實際過了 {passed} 題：完全猜中！"
    elif abs(gap) == 1:
        text = f"你猜 {predicted} 題，實際過了 {passed} 題：差 1 題，很準。"
    elif gap > 0:
        text = f"你猜 {predicted} 題，實際過了 {passed} 題：高估了 {gap} 題（猜的比實際多）。"
    else:
        text = f"你猜 {predicted} 題，實際過了 {passed} 題：低估了 {-gap} 題（其實你比自己想的好）。"
    return text, pct


def practice_days(records: state.Records) -> int:
    """有練習的天數：跑過課號檢查、或答過回顧題的不同日子。"""
    days = {state.day_of(a["time"]) for a in records.read("attempts") if a.get("time")}
    days |= {state.day_of(r["time"]) for r in records.read("reviews") if r.get("time")}
    return len(days)


def passed_reach(prog: dict, order: list[str]) -> int:
    """通過的課裡，排在課表最後面的那一課的位置（還沒通過任何一課是 -1）。"""
    idx = [order.index(lid) for lid, info in prog["lessons"].items() if info.get("first_pass") and lid in order]
    return max(idx, default=-1)


def record_timing(lesson: grader.Lesson, outcome: grader.Outcome, info: dict) -> None:
    timed = lesson.meta.get("timed", {})
    for r in outcome.results:
        rule = timed.get(r.id)
        if not rule or not r.ok or "minutes" not in r.data:
            continue
        mine = info.setdefault("timed", {})
        if r.id in mine:
            continue
        minutes = r.data["minutes"]
        mine[r.id] = minutes
        standard = rule.get("standard")
        line = f"{rule.get('label', r.id)}：照檔案時間算，大約花了{grader.spaced(fmt_minutes(minutes))}"
        if standard:
            line += f"（標準是 {standard} 分鐘內）。"
            line += "做到了！" if minutes <= standard else "這次先記下來，多練幾次就會變快。"
        print(line)


def cmd_lesson(raw: str, opts: dict) -> int:
    lesson = find_lesson(raw)
    if lesson is None:
        return 1
    ledger = get_ledger()
    if ledger is None:
        return 1
    records = state.Records(ledger)
    records.ensure()
    info_course = course()
    order = grader.course_order(info_course)
    gate = bool(lesson.meta.get("gate"))

    print(f"━━ {lesson.id}  {lesson.title} ━━")
    if lesson.meta.get("minutes"):
        print(f"這課大約要花 {lesson.meta['minutes']} 分鐘。")

    planned = grader.plan(lesson, ledger)
    total = len(planned)
    try:
        predicted = get_prediction(total, opts)  # 行為 1
    except BadPrediction as exc:
        print(exc)
        return 2

    t = state.now()
    now_iso = t.isoformat(timespec="seconds")
    prog = records.progress()
    info = prog["lessons"].setdefault(lesson.id, {})
    info.setdefault("first_run", now_iso)
    info["runs"] = info.get("runs", 0) + 1

    print()
    outcome = grader.evaluate(lesson, ledger)
    passed, total = outcome.passed, outcome.total
    stages = lesson.meta.get("stages") if gate else None
    show_outcome(outcome, opts["all"], stages)  # 行為 2

    records.append("attempts", {
        "time": now_iso,
        "lesson": lesson.id,
        "predicted": predicted,
        "passed": passed,
        "total": total,
        "failed": [r.id for r in outcome.results if not r.ok],
    })
    info["last_run"] = now_iso
    info["last_result"] = [passed, total]
    all_ok = passed == total and total > 0

    print()
    record_timing(lesson, outcome, info)
    stages_done = False
    if stages:
        stage_info = info.setdefault("stages", {})
        for stage in stages:
            rows = [r for r in outcome.results if r.stage == stage]
            if rows and all(r.ok for r in rows):
                stage_info.setdefault(stage, now_iso)
        stages_done = all(s in stage_info for s in stages)
    newly = (all_ok or stages_done) and not info.get("first_pass")

    if all_ok:
        print(f"✓ 全部 {total} 題都過了！")
    if newly:
        info["first_pass"] = now_iso
        no_start = not info.get("start")
        base = min((x for x in (info.get("first_run"), info.get("start")) if x), key=state.parse_time)
        spent = minutes_between(base, now_iso)  # 行為 3
        print(f"從{'開始這課' if base == info.get('start') else '第一次跑檢查'}到這次全過，一共{grader.spaced(fmt_minutes(spent))}。")
        limit = float(lesson.meta.get("fast_minutes", 0))
        if limit and spent < limit and no_start and info["runs"] == 1:
            print(f"（下次開始一課之前，先打 uv run check.py start {lesson.id}，這樣才算得出你花了多久。）")
        elif limit and spent < limit:
            info["fast_warning_minutes"] = round(spent, 1)
            print()
            print(f"⚠ 這是警訊：不到{grader.spaced(fmt_minutes(limit))}就全部做對。")
            print("  如果是你自己做的，很好，這段可以忽略。")
            if gate:
                print("  如果剛剛有用 AI：關卡要關掉 AI 自己做，請關掉 AI 再做一次。")
            else:
                print("  如果是 AI 幫你寫的：第①圈的目的是讓你自己練，請關掉 AI 再寫一次。")
            print("  （這只是提醒，不扣分，也不擋你往下走。）")
    elif all_ok and info.get("first_pass"):
        print(f"（你在 {mmdd(info['first_pass'])} 就第一次全過了，這次是複習。）")

    if stages:
        print("關卡進度：" + "  ".join(f"{s} {'✓' if s in info['stages'] else '✗'}" for s in stages))

    if lesson.id in order:
        prog["frontier"] = max(prog.get("frontier", -1), order.index(lesson.id))
    records.save_progress(prog)

    if predicted is not None:
        text, pct = calibration_line(predicted, passed, total)
        print(text)
        pre = info.get("pre_prediction")
        if pre is not None and stages:
            print(f"（開始前你猜 {pre} 題，做完猜 {predicted} 題，實際 {passed} 題。）")
        if abs(pct) >= BIG_GAP:
            print("這次猜的跟實際差比較多。寫一句：下次我會怎麼估？")
            if interactive():
                sentence = ask("下次我會：")
                if sentence and sentence.strip():
                    records.append("notes", {"time": now_iso, "lesson": lesson.id, "text": sentence.strip()})
                    print("記下來了。")
            else:
                print('  打：uv run check.py note "下次我會……"')

    if stages_done:
        days = practice_days(records)
        need = int(lesson.meta.get("gate_days", 3))
        level = lesson.meta.get("level_name", "這一級")
        if info.get("level_up"):
            print(f"（{level}在 {mmdd(info['level_up'])} 就過關了。）")
        elif days >= need:
            info["level_up"] = now_iso
            records.save_progress(prog)
            print(f"★ {level}過關！練習了 {days} 天，可以升級了。")
        else:
            print(f"三關都過了！練習天數 {days}／{need} 天，再練 {need - days} 天就升級"
                  "（跑課號檢查或答回顧題，不同天都算）。")

    if not opts["no_review"]:
        offer_reviews(records, current=lesson.id)  # 行為 4
    return 0 if all_ok else 1


# ====================================================================
# 行為 4：間隔回顧
# ====================================================================

def review_candidates(records: state.Records) -> list[dict]:
    """所有已經到期、還沒長成葉子的（課, 時段）。到期＝通過的課已經往後走了 2 課（或 5 課）。"""
    order = grader.course_order(course())
    prog = records.progress()
    rows = records.read("reviews")
    reach = passed_reach(prog, order)
    out = []
    for lid, info in prog["lessons"].items():
        if not info.get("first_pass") or lid not in order:
            continue
        try:
            lesson = grader.load_lesson(lid, ROOT)
        except grader.LessonNotFound:
            continue
        questions = lesson.review_questions()
        if not questions:
            continue
        idx = order.index(lid)
        for slot_no, k in enumerate(SLOTS):
            if reach < idx + k:
                continue
            mine = [r for r in rows if r.get("lesson") == lid and r.get("slot") == k]
            if any(r.get("leaf") for r in mine):
                continue
            out.append({
                "lesson": lid,
                "slot": k,
                "slot_no": slot_no,
                "order": idx,
                "tries": len(mine),  # 每答一次（答錯、或同一天答對）就換下一題
                "questions": questions,
                "pass_day": state.day_of(info["first_pass"]),
            })
    return out


def due_reviews(records: state.Records, current: str | None = None) -> list[dict]:
    """這次要問的回顧題：最多兩題，「2 課前」一題、「5 課前」一題。

    先挑正在檢查的這課往前數第 2 課、第 5 課；沒有的話，挑積欠最久的。其他的留到下次。
    """
    order = grader.course_order(course())
    cands = review_candidates(records)
    if not cands:
        return []
    anchor = order.index(current) if current in order else passed_reach(records.progress(), order)
    picked: list[dict] = []
    for slot_no, k in enumerate(SLOTS):
        pool = [c for c in cands if c["slot"] == k]
        if not pool:
            continue
        exact = [c for c in pool if c["order"] == anchor - k]
        choice = exact[0] if exact else min(pool, key=lambda c: c["order"])
        qs = choice["questions"]
        pos = (choice["slot_no"] + choice["tries"]) % len(qs)
        q = qs[pos]
        if any(p["lesson"] == choice["lesson"] and p["q"]["id"] == q["id"] for p in picked) and len(qs) > 1:
            q = qs[(pos + 1) % len(qs)]
        picked.append(dict(choice, q=q, id=f"{choice['lesson']}:{q['id']}"))
    return picked


def leaves(records: state.Records) -> int:
    return len({(r["lesson"], r["slot"]) for r in records.read("reviews") if r.get("leaf")})


def review_answer_ok(q: dict, answer: str) -> bool:
    kind = q.get("normalize", "text")
    home = q.get("home")
    accepted = {grader.norm_answer(a, kind, home) for a in q["accept"]}
    if q.get("choices"):
        letter = grader.pick_choice(answer, q["choices"])
        return letter is not None and grader.norm_answer(letter, kind, home) in accepted
    return grader.norm_answer(answer, kind, home) in accepted


def answer_review(records: state.Records, item: dict, answer: str) -> bool:
    q = item["q"]
    ok = review_answer_ok(q, answer)
    t = state.now()
    leaf = ok and t.date().isoformat() != item["pass_day"]
    records.append("reviews", {
        "time": t.isoformat(timespec="seconds"),
        "lesson": item["lesson"],
        "slot": item["slot"],
        "qid": q["id"],
        "answer": answer,
        "correct": ok,
        "leaf": leaf,
    })
    if ok and leaf:
        print("✓ 答對了！技能樹長出一片葉子（跟上課不同天答對才算）。")
    elif ok:
        print(f"✓ 答對了。不過今天跟你通過 {item['lesson']} 是同一天，先不算葉子；明天以後會換一題再問你。")
    else:
        right = q["accept"][0]
        if q.get("choices") and right in q["choices"]:
            right = f"{right}（{q['choices'][right]}）"
        print("✗ 這題先算錯，下次會換一題再問你。")
        print(f"  正確答案：{right}")
    if q.get("explain"):
        print(f"  {q['explain']}")
    return ok


def print_due(items: list[dict]) -> None:
    for d in items:
        print(f"  [{d['id']}]（複習 {d['lesson']}）")
        for line in d["q"]["q"].splitlines():
            print(f"    {line}")


def ask_reviews(records: state.Records, items: list[dict]) -> None:
    for d in items:
        print_due([d])
        ans = ask("  你的答案（直接按 Enter 先跳過）：")
        if ans and ans.strip():
            answer_review(records, d, ans.strip())


def offer_reviews(records: state.Records, current: str | None = None) -> None:
    items = due_reviews(records, current)
    if not items:
        return
    today = state.now().date().isoformat()
    prog = records.progress()
    print()
    if prog.get("review_asked") == today:
        print(f"今天還有 {len(items)} 題回顧題沒答（打 uv run check.py review 作答）。")
        return
    print(f"今天到期的回顧題（{len(items)} 題）：")
    if interactive():
        prog["review_asked"] = today
        records.save_progress(prog)
        ask_reviews(records, items)
    else:
        print_due(items)
        print("作答：uv run check.py review <題號> <你的答案>，例如 uv run check.py review " + items[0]["id"] + " 你的答案")


def cmd_review(args: list[str]) -> int:
    ledger = get_ledger()
    if ledger is None:
        return 1
    records = state.Records(ledger)
    items = due_reviews(records)
    if not args:
        if not items:
            print(f"今天沒有到期的回顧題。技能樹的葉子：{leaves(records)} 片。")
            return 0
        print(f"今天到期的回顧題（{len(items)} 題）：")
        if interactive():
            ask_reviews(records, items)
        else:
            print_due(items)
            print("作答：uv run check.py review <題號> <你的答案>")
        return 0
    qid = args[0]
    answer = " ".join(args[1:]).strip()
    match = [d for d in items if d["id"] == qid]
    if not match:
        print(f"{qid} 現在沒有到期（或是已經長成葉子了）。打 uv run check.py review 看今天有哪些。")
        return 1
    if not answer:
        print("要附上你的答案，例如：uv run check.py review " + qid + " 你的答案")
        return 2
    return 0 if answer_review(records, match[0], answer) else 1


# ====================================================================
# note：下次我會怎麼估
# ====================================================================

def cmd_note(args: list[str]) -> int:
    ledger = get_ledger()
    if ledger is None:
        return 1
    text = " ".join(args).strip()
    if not text:
        print('要寫一句話，例如：uv run check.py note "下次我會先跑一次自己的檢查再猜"')
        return 2
    records = state.Records(ledger)
    attempts = records.read("attempts")
    records.append("notes", {
        "time": state.now().isoformat(timespec="seconds"),
        "lesson": attempts[-1]["lesson"] if attempts else None,
        "text": text,
    })
    print("記下來了。下次猜之前想想這句話。")
    return 0


# ====================================================================
# status
# ====================================================================

def calibration_rows(records: state.Records) -> list[dict]:
    return [a for a in records.read("attempts") if a.get("predicted") is not None and a.get("total")]


def curve_line(a: dict) -> str:
    pct = (a["predicted"] - a["passed"]) * 100 / a["total"]
    n = min(10, round(abs(pct) / 10))
    left = ("█" * n).rjust(10) if pct < 0 else " " * 10
    right = ("█" * n).ljust(10) if pct > 0 else " " * 10
    return f"  {mmdd(a['time']):>5} {a['lesson']:<4} {left}│{right} {pct:+.0f}%（猜 {a['predicted']}，過 {a['passed']}／{a['total']}）"


def recent_summary(recent: list[dict]) -> str:
    gaps = [(a["predicted"] - a["passed"]) * 100 / a["total"] for a in recent]
    mean_abs = sum(abs(g) for g in gaps) / len(gaps)
    if round(mean_abs) == 0:
        return f"  最近 {len(recent)} 次都猜中了。"
    over = sum(1 for g in gaps if g > 0)
    under = sum(1 for g in gaps if g < 0)
    lean = "大多是高估（猜的比實際多）" if over > under else "大多是低估（其實你比自己想的好）" if under > over else "高估和低估差不多"
    return f"  最近 {len(recent)} 次平均差 {mean_abs:.0f}%，{lean}。"


def cmd_status() -> int:
    ledger = get_ledger()
    if ledger is None:
        return 1
    records = state.Records(ledger)
    prog = records.progress()
    info_course = course()
    titles = grader.course_titles(info_course)
    order = grader.course_order(info_course)
    ready = set(grader.available_lessons(ROOT))
    lessons = prog["lessons"]

    print("PyPy 熊的進度")
    print(f"帳本：{ledger}")
    print("─" * 40)
    for level in info_course["levels"]:
        a, b = order.index(level["first"]), order.index(level["last"])
        ids = [lid for lid in order[a: b + 1] if lid in ready or lid in lessons]
        if not ids:
            continue
        print(level["name"])
        for lid in ids:
            info = lessons.get(lid, {})
            title = titles.get(lid, lid)
            if info.get("first_pass"):
                mark, extra = "✓", f"{mmdd(info['first_pass'])} 通過"
            elif info.get("runs"):
                p, t = info.get("last_result", [0, 0])
                mark, extra = "✗", f"跑了 {info['runs']} 次，最近一次 {p}／{t}"
            elif info.get("start"):
                mark, extra = "·", "開始了，還沒跑檢查"
            else:
                mark, extra = "·", "還沒開始"
            stages = info.get("stages")
            if stages is not None:
                try:
                    names = grader.load_lesson(lid, ROOT).meta.get("stages", [])
                except grader.LessonNotFound:
                    names = list(stages)
                extra += "；" + " ".join(f"{s}{'✓' if s in stages else '✗'}" for s in names)
                if info.get("level_up"):
                    extra += "；已升級"
            for rid, minutes in info.get("timed", {}).items():
                extra += f"；重建花了{grader.spaced(fmt_minutes(minutes))}" if "rebuild" in rid else ""
            print(f"  {mark} {lid:<4} {title}　{extra}")
    print()
    print(f"練習天數：{practice_days(records)} 天（跑課號檢查或答回顧題的不同日子）")
    due = due_reviews(records)
    waiting = len(review_candidates(records)) - len(due)
    if due:
        more = f"；另外還有 {waiting} 題排隊，之後會輪到" if waiting > 0 else ""
        print(f"今天到期的回顧題：{len(due)} 題（打 uv run check.py review 作答{more}）")
    else:
        print("今天到期的回顧題：沒有")
    print(f"技能樹的葉子：{leaves(records)} 片")
    fast = [f"{lid}（{fmt_minutes(info['fast_warning_minutes'])}）" for lid, info in lessons.items()
            if info.get("fast_warning_minutes") is not None]
    if fast:
        print("太快全對的警訊：" + "、".join(fast))

    rows = calibration_rows(records)
    print()
    if rows:
        print("校準曲線（你猜的 − 實際；右邊是高估，左邊是低估）：")
        print("              低估 ◀────────┼────────▶ 高估")
        for a in rows[-10:]:
            print(curve_line(a))
        print(recent_summary(rows[-5:]))
        notes = records.read("notes")
        if notes:
            print(f"  你寫過的「下次我會怎麼估」：{notes[-1]['text']}")
    else:
        print("校準曲線：還沒有資料（每次檢查前猜一下會過幾題，這裡就會畫出來）。")

    passed = {lid for lid, info in lessons.items() if info.get("first_pass")}
    prog_bar = concept_map.progress(concept_map.SHOWCASE.read_text(encoding="utf-8"), passed)
    print()
    print(f"看得懂進度條：[{concept_map.bar(prog_bar.percent)}] {prog_bar.percent}%"
          f"（showcase 帳本 {prog_bar.total} 行，你看得懂 {prog_bar.understood} 行）")
    unreleased = [lid for lid in order[: max(prog.get("frontier", -1), 0) + 1] if lid not in ready]
    if unreleased and prog_bar.percent < 100:
        print("  有些課還沒上架；上架後通過了，進度條才會算進去。")
    return 0


# ====================================================================

def main(argv: list[str] | None = None) -> int:
    setup_streams()
    pos, opts = parse_args(sys.argv[1:] if argv is None else argv)
    if not pos or pos[0] == "help":
        print(HELP)
        return 0
    cmd, rest = pos[0], pos[1:]
    try:
        if cmd == "setup":
            return cmd_setup(rest)
        if cmd == "status":
            return cmd_status()
        if cmd == "review":
            return cmd_review(rest)
        if cmd == "start":
            return cmd_start(rest, opts)
        if cmd == "note":
            return cmd_note(rest)
        return cmd_lesson(cmd, opts)
    except BadPrediction as exc:
        print(exc)
        return 2
    except KeyboardInterrupt:
        print("\n（停下來了，沒關係。）")
        return 130
    except Exception as exc:  # noqa: BLE001 - 最後一道防線：不要噴一大串錯誤嚇到新手
        if os.environ.get("PLUSFORM_DEBUG"):
            raise
        print()
        print(f"check.py 自己出了意料之外的錯（這不是你的錯）：{type(exc).__name__}: {exc}")
        print("麻煩把這段訊息和你打的指令一起回報給課程。想看完整的錯誤訊息，在指令前面加 PLUSFORM_DEBUG=1 再跑一次。")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
