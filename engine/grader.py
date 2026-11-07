"""判分引擎：讀每課的 tests/checks.json，一項一項檢查。

check.py（學員端）和 tools/validate_lesson.py（老師端）共用這一份。
只用 Python 標準庫；絕不呼叫任何 AI 或網路服務（帳本的 uv 也加 --offline，不讓它連網）。

檢查的種類（checks.json 裡每一項的 "type"）：
  tree          帳本裡應該有／不該有哪些資料夾和檔案
  answers       對答：學員在「答：」後面寫的答案，對照 answers/ 的固定答案
  uv_project    帳本是 uv 專案（有 pyproject.toml）
  python_pin    帳本把 Python 釘在指定版本（.python-version）
  uv_python     帳本用的是自己 .venv 裡的 Python，不是系統 Python
  run           在帳本的環境裡跑學員的程式（stdin 由這裡餵），比對印出來的字
  call          呼叫學員寫的函式，比對回傳值
  chaff         wheat/chaff：學員寫的檢查要在正確版全過、在每個壞版本至少錯一條
  script_match  學員改過的腳本，在假的資料夾裡跑起來要跟安全版一樣
  git_commits   帳本是 git 存放庫，而且至少有幾個存檔點（commit）

學員寫的檔案一律用 utf-8-sig 讀（Windows 記事本會在最前面加看不見的 BOM），
讀不懂（例如存成 Big5）就給白話的說明，不噴 Traceback。
"""

from __future__ import annotations

import ast
import io
import json
import os
import re
import secrets
import shutil
import sys
import tokenize
import tomllib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from . import proc as procs
from . import vshell

ENGINE_DIR = Path(__file__).resolve().parent
COURSE_ROOT = ENGINE_DIR.parent
RUNNER = ENGINE_DIR / "runner.py"
MARK = "@@PLUSFORM@@"
SPECIAL_MARKS = ("已知會當掉", "需求有問題")
WARMUP_TIMEOUT = 180.0
DASHES = str.maketrans({c: "-" for c in "‐‑‒–—―−－﹣"})


# ====================================================================
# 課程與課號
# ====================================================================

def course_info(root: Path = COURSE_ROOT) -> dict:
    return json.loads((root / "course.json").read_text(encoding="utf-8"))


def normalize_id(raw: str, course: dict) -> str:
    text = unicodedata.normalize("NFKC", raw).translate(DASHES).strip()
    alias = course.get("aliases", {}).get(text.lower())
    if alias:
        return alias
    m = re.fullmatch(r"(\d+)-0*(\d+)", text)
    if m:
        return f"{int(m.group(1))}-{int(m.group(2))}"
    m = re.fullmatch(r"(\d+)-[cC](\d*)", text)
    if m:
        return f"{int(m.group(1))}-C{m.group(2)}"
    return text


def course_order(course: dict) -> list[str]:
    return [entry["id"] for entry in course["lessons"]]


def course_titles(course: dict) -> dict[str, str]:
    return {entry["id"]: entry["title"] for entry in course["lessons"]}


def available_lessons(root: Path = COURSE_ROOT) -> list[str]:
    course = course_info(root)
    return [lid for lid in course_order(course) if (root / "lessons" / lid / "lesson.json").is_file()]


@dataclass
class Lesson:
    id: str
    dir: Path
    meta: dict
    checks: list[dict]

    @property
    def title(self) -> str:
        return self.meta.get("title", self.id)

    def path(self, rel: str) -> Path:
        return self.dir / rel

    def review_questions(self) -> list[dict]:
        path = self.dir / "review" / "questions.json"
        if not path.is_file():
            return []
        return json.loads(path.read_text(encoding="utf-8")).get("questions", [])


class LessonNotFound(Exception):
    pass


def load_lesson(lesson_id: str, root: Path = COURSE_ROOT) -> Lesson:
    folder = root / "lessons" / lesson_id
    meta_path = folder / "lesson.json"
    if not meta_path.is_file():
        raise LessonNotFound(lesson_id)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    checks_path = folder / "tests" / "checks.json"
    checks = json.loads(checks_path.read_text(encoding="utf-8"))["checks"] if checks_path.is_file() else []
    return Lesson(id=lesson_id, dir=folder, meta=meta, checks=checks)


# ====================================================================
# 結果
# ====================================================================

@dataclass
class Result:
    id: str
    group: str
    desc: str
    stage: str | None = None
    ok: bool = False
    detail: str = ""  # 沒過的時候，給新手看的說明
    note: str = ""  # 過了也想說的話
    special: bool = False  # 學員標了「已知會當掉／需求有問題」的那幾條
    data: dict = field(default_factory=dict)  # 給 check.py 記錄用（例如重建花了幾分鐘）


@dataclass
class Outcome:
    results: list[Result]
    summaries: list[str] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def total(self) -> int:
        return len(self.results)


class NotReady(Exception):
    """還不能檢查（訊息直接給學員看）。"""


class RunnerTrouble(Exception):
    """跑程式時出狀況（訊息直接給學員看）。"""


# ====================================================================
# 讀學員的檔案
# ====================================================================

ENCODING_HELP = (
    "用 VS Code 打開它，點視窗右下角的編碼（可能寫著 Big5），選「以編碼儲存」→「UTF-8」，再跑一次。"
)


def read_student_text(path: Path) -> str:
    """讀學員寫的檔案：去掉 BOM、換行統一；不是 UTF-8 就給白話說明。"""
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise NotReady(f"{path.name} 不是用 UTF-8 存的，check.py 讀不懂。{ENCODING_HELP}") from None
    except OSError as exc:
        raise NotReady(f"打不開 {path.name}：{exc.strerror or exc}") from None


def has_crlf(path: Path) -> bool:
    try:
        return b"\r" in path.read_bytes()
    except OSError:
        return False


CRLF_HELP = (
    "這個檔案是 Windows 的換行（CRLF），bash 跑起來會建出名字最後多一個看不見字元的資料夾。"
    "用 VS Code 打開它，點視窗右下角的「CRLF」改成「LF」，存檔後再試一次。"
)


# ====================================================================
# 怎麼跑 Python
# ====================================================================

def find_uv() -> str | None:
    env_uv = os.environ.get("UV")
    if env_uv and Path(env_uv).is_file():
        return env_uv
    found = shutil.which("uv")
    if found:
        return found
    exe = "uv.exe" if os.name == "nt" else "uv"
    for cand in (Path.home() / ".local" / "bin" / exe, Path.home() / ".cargo" / "bin" / exe):
        if cand.is_file():
            return str(cand)
    return None


def child_env() -> dict:
    env = dict(os.environ)
    env.pop("VIRTUAL_ENV", None)  # 外層 uv run check.py 留下的，帳本要用自己的 .venv
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


Proc = procs.Proc


@dataclass
class Reply:
    """runner 回來的東西：最後的結果（被收掉的話是 None）、一路上的進度、程序本身。"""
    result: dict | None
    events: list[tuple[str, str]]
    proc: Proc


class Env:
    """學員端在帳本的環境裡跑；老師端（local=True）用目前這個 Python。

    學員端第一次要跑程式時，先用 uv run --offline 暖身一次（不計入逾時，也不連網），
    問出帳本 .venv 裡那支 Python 在哪裡，之後就直接用它跑：比較快，逾時也殺得到它本人。
    """

    def __init__(self, ledger: Path | None, local: bool = False, timeout: float = 30.0,
                 cap: int = procs.DEFAULT_CAP):
        self.ledger = ledger
        self.local = local
        self.timeout = timeout
        self.cap = cap
        self._probe: dict | None = None

    def cwd(self) -> Path:
        return self.ledger if self.ledger else Path.cwd()

    def probe(self) -> dict:
        if self._probe is not None:
            return self._probe
        if self.local:
            reply = self._run_runner([sys.executable, "-B"], {"op": "probe"}, self.timeout)
            if reply.result is None or "executable" not in reply.result:
                raise RunnerTrouble("老師端的 Python 跑不起來。")
            self._probe = reply.result
            return self._probe
        if self.ledger is None:
            raise NotReady("還不知道你的帳本在哪裡。先打：uv run check.py setup ~/code/ledger")
        if not (self.ledger / "pyproject.toml").is_file():
            raise NotReady(
                "你的帳本還不是 uv 專案（找不到 pyproject.toml）。"
                "先完成 0-5：在帳本資料夾裡打 uv init --no-package --vcs none --python 3.13"
            )
        uv = find_uv()
        if not uv:
            raise NotReady("找不到 uv 這個指令。先完成 0-5 的安裝，再開一個新的終端機視窗試試看。")
        cmd = [uv, "run", "--quiet", "--no-progress", "--offline", "python", "-B"]
        reply = self._run_runner(cmd, {"op": "probe"}, WARMUP_TIMEOUT)
        if reply.result is None or "executable" not in reply.result:
            raise NotReady(
                "uv 沒辦法在你的帳本裡把 Python 跑起來（check.py 不會讓 uv 連網）。\n"
                "  先到帳本資料夾裡打一次 uv run main.py，看看它說什麼（第一次可能要連網下載 Python），再回來跑檢查。\n"
                "  uv 的訊息最後幾行：\n" + tail(reply.proc.stderr)
            )
        self._probe = reply.result
        return self._probe

    def python_cmd(self) -> list[str]:
        if self.local:
            return [sys.executable]
        return [self.probe()["executable"]]

    def run_file(self, path: Path, stdin: str = "", cwd: Path | None = None, timeout: float | None = None) -> Proc:
        cmd = self.python_cmd() + ["-B", str(path)]
        return procs.run(cmd, stdin=stdin, cwd=cwd or self.cwd(), env=child_env(),
                         timeout=timeout or self.timeout, cap=self.cap)

    def _run_runner(self, cmd: list[str], request: dict, timeout: float) -> Reply:
        token = secrets.token_hex(8)
        payload = dict(request, token=token)
        p = procs.run(cmd + [str(RUNNER)], stdin=json.dumps(payload, ensure_ascii=False), cwd=self.cwd(),
                      env=child_env(), timeout=timeout, cap=self.cap)
        prefix = f"{MARK}{token}@@"
        events: list[tuple[str, str]] = []
        result = None
        for line in p.stdout.splitlines():
            if not line.startswith(prefix):
                continue
            kind, _, rest = line[len(prefix):].partition(" ")
            if kind == "result":
                try:
                    result = json.loads(rest)
                except ValueError:
                    result = None
            else:
                events.append((kind, rest))
        return Reply(result=result, events=events, proc=p)

    def runner_raw(self, request: dict, timeout: float | None = None) -> Reply:
        return self._run_runner(self.python_cmd() + ["-B"], request, timeout or self.timeout)

    def runner(self, request: dict, timeout: float | None = None) -> dict:
        reply = self.runner_raw(request, timeout)
        if reply.result is None:
            if reply.proc.timed_out:
                raise RunnerTrouble(f"跑了 {timeout or self.timeout:.0f} 秒還沒結束，可能有無窮迴圈。")
            if reply.proc.overflow:
                raise RunnerTrouble("你的程式印了太多東西，被停下來了：可能是迴圈沒停下來。")
            raise RunnerTrouble("檢查程式沒有正常結束。錯誤訊息最後幾行：\n" + tail(reply.proc.stderr))
        if "runner_error" in reply.result:
            raise RunnerTrouble("檢查程式出錯了：" + reply.result["runner_error"])
        return reply.result


# ====================================================================
# 小工具
# ====================================================================

def tail(text: str, n: int = 6) -> str:
    lines = [ln for ln in _text(text).rstrip().splitlines() if ln.strip()]
    return "\n".join("    " + ln for ln in lines[-n:])


def show(value) -> str:
    if isinstance(value, str):
        return f"「{value}」"
    return repr(value)


def norm_line(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split())


def norm_answer(text: str, kind: str = "text", home: str | None = None) -> str:
    text = unicodedata.normalize("NFKC", text).strip()
    text = text.strip("`'\"「」『』")
    if kind == "path":
        text = text.replace("\\", "/").strip()
        if home and (text == "~" or text.startswith("~/")):
            text = home + text[1:]
        return text.rstrip("/") or "/"
    return "".join(text.split()).lower()


CHOICE_LEAD = re.compile(r"^\s*[(（]?([A-Za-z])\s*(?:[)）.、．:：,，]|\s|$)")


def pick_choice(given: str, choices: dict) -> str | None:
    """選擇題：「B」「b」「B. PATH 還沒更新」「(B)」都當成 B；照抄選項文字也認得。"""
    text = unicodedata.normalize("NFKC", given).strip().strip("`'\"「」『』")
    letters = {k.upper() for k in choices}
    m = CHOICE_LEAD.match(text)
    if m and m.group(1).upper() in letters:
        return m.group(1).upper()
    flat = "".join(text.split()).lower()
    for k, v in choices.items():
        if flat and flat == "".join(unicodedata.normalize("NFKC", v).split()).lower():
            return k.upper()
    return None


def or_list(items: list[str]) -> str:
    """["A", "B", "C"] → 「A、B 或 C」。"""
    if len(items) <= 1:
        return "".join(items)
    return "、".join(items[:-1]) + " 或 " + items[-1]


def args_text(args: list) -> str:
    return ", ".join(repr(a) for a in args)


def output_lines(text: str) -> list[str]:
    return [norm_line(ln) for ln in _text(text).splitlines() if ln.strip()]


def first_problem(problems: list[str]) -> str:
    if not problems:
        return ""
    more = f"\n  （一共有 {len(problems)} 個地方不對，這是第一個）" if len(problems) > 1 else ""
    return problems[0] + more


def show_stdin(stdin: str) -> str:
    parts = stdin.split("\n")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return "、".join(parts) if parts else "（什麼都不輸入）"


def spaced(text: str) -> str:
    """數字開頭的前面空一格（「一共 40 分鐘」），中文開頭的不空（「一共不到 1 分鐘」）。"""
    return (" " + text) if text[:1].isdigit() else text


# ====================================================================
# 檢查項目
# ====================================================================

DEFAULT_GROUP = {
    "tree": "官方測試",
    "answers": "對答",
    "uv_project": "官方測試",
    "python_pin": "官方測試",
    "uv_python": "官方測試",
    "run": "官方測試",
    "call": "官方測試",
    "chaff": "第三圈",  # 終端機輸出不用圈號字元：③ 在 xterm.js、Terminal.app 會跟下一個字疊在一起
    "script_match": "官方測試",
    "git_commits": "官方測試",
}


@dataclass
class Ctx:
    lesson: Lesson
    ledger: Path | None
    env: Env
    overrides: dict[str, Path] = field(default_factory=dict)
    summaries: list[str] = field(default_factory=list)
    _call_cache: dict = field(default_factory=dict)
    stuck: dict = field(default_factory=dict)  # 同一支程式剛剛跑不完，就不要每題再各等一次

    def student(self, rel: str) -> Path:
        if rel in self.overrides:
            return self.overrides[rel]
        if self.ledger is None:
            raise NotReady("還不知道你的帳本在哪裡。先打：uv run check.py setup ~/code/ledger")
        return self.ledger / rel

    def course(self, rel: str) -> Path:
        return self.lesson.path(rel)

    def missing(self, rel: str, hint: str | None = None) -> str:
        hint = hint or self.lesson.meta.get("missing_hint")
        if hint:
            return f"找不到 {rel}。{hint}"
        return f"找不到 {rel}。先打：uv run check.py start {self.lesson.id}，把這課的起點檔複製到帳本。"


class Check:
    def __init__(self, spec: dict, ctx: Ctx):
        self.spec = spec
        self.ctx = ctx
        self.group = spec.get("group") or DEFAULT_GROUP.get(spec["type"], "官方測試")
        self.stage = spec.get("stage")

    def stub(self, suffix: str | None, desc: str) -> Result:
        rid = self.spec["id"] + (f"-{suffix}" if suffix else "")
        return Result(id=rid, group=self.group, desc=desc, stage=self.stage)

    def plan(self) -> list[Result]:
        return [self.stub(None, self.spec.get("desc", self.spec["id"]))]

    def run(self, results: list[Result]) -> None:
        raise NotImplementedError


# ---------------- tree ----------------

def parse_tree_spec(text: str) -> list[tuple[bool, str]]:
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("沒有"):
            out.append((False, line[2:].strip()))
        else:
            out.append((True, line))
    return out


def build_minutes(base: Path) -> float | None:
    """照檔案時間估一個資料夾「從建立到最後一次改動」花了幾分鐘（誠實制，只是參考）。"""
    try:
        times = []
        for p in [base, *base.rglob("*")]:
            st = p.stat()
            times.append(st.st_mtime)
        st = base.stat()
        start = getattr(st, "st_birthtime", None) or min(times)
        end = max(times)
        return max(end - start, 0) / 60
    except OSError:
        return None


class TreeCheck(Check):
    def run(self, results):
        r = results[0]
        root_rel = self.spec.get("root", ".")
        base = self.ctx.student(root_rel)
        entries = parse_tree_spec(self.ctx.course(self.spec["spec"]).read_text(encoding="utf-8"))
        problems = []
        if not base.is_dir():
            problems.append(f"找不到資料夾 {root_rel}")
        else:
            for must, rel in entries:
                path = base / rel.rstrip("/")
                want_dir = rel.endswith("/")
                if must:
                    if not path.exists():
                        odd = path.with_name(path.name + "\r")
                        if odd.exists():
                            problems.append(f"找不到 {rel}，可是有一個名字最後多了看不見字元的 {rel}。{CRLF_HELP}")
                        else:
                            problems.append(f"找不到 {rel}（應該要有這個{'資料夾' if want_dir else '檔案'}）")
                    elif want_dir and not path.is_dir():
                        problems.append(f"{rel} 應該是資料夾，可是它是檔案")
                    elif not want_dir and path.is_dir():
                        problems.append(f"{rel} 應該是檔案，可是它是資料夾")
                elif path.exists():
                    problems.append(f"{rel} 應該已經刪掉了，可是還在")
        r.ok = not problems
        hint = self.spec.get("hint", "")
        r.detail = first_problem(problems) + (f"\n  {hint}" if hint and problems else "")
        if r.ok and self.spec.get("time_it"):
            minutes = build_minutes(base)
            if minutes is not None:
                r.data["minutes"] = round(minutes, 1)


# ---------------- answers ----------------

ANSWER_LINE = re.compile(r"^\s*答\s*[:：]\s*(.*?)\s*$")


def read_answer_lines(path: Path) -> list[str]:
    out = []
    for raw in read_student_text(path).splitlines():
        m = ANSWER_LINE.match(raw)
        if m:
            out.append(m.group(1))
    return out


class AnswersCheck(Check):
    def key(self) -> dict:
        return json.loads(self.ctx.course(self.spec["key"]).read_text(encoding="utf-8"))

    def plan(self):
        out = []
        for i, q in enumerate(self.key()["questions"], start=1):
            title = q.get("title") or q.get("desc") or q["id"]
            out.append(self.stub(q["id"], f"對答第 {i} 題（{title}）"))
        return out

    def run(self, results):
        key = self.key()
        rel = self.spec["file"]
        path = self.ctx.student(rel)
        if not path.is_file():
            for r in results:
                r.detail = self.ctx.missing(rel)
            return
        answers = read_answer_lines(path)
        kind = key.get("normalize", "text")
        home = key.get("home")
        choices = key.get("choices")
        how = key.get("how") or (or_list(sorted(choices)) if choices else "你的答案")
        for i, (r, q) in enumerate(zip(results, key["questions"]), start=1):
            given = answers[i - 1] if i - 1 < len(answers) else ""
            if not given.strip():
                r.detail = f"還沒作答：打開帳本裡的 {rel}，在第 {i} 題的「答：」後面寫{how}，存檔。"
                continue
            accepted = {norm_answer(a, kind, home) for a in q["accept"]}
            if choices:
                letter = pick_choice(given, choices)
                if letter is None:
                    r.detail = f"你寫「{given.strip()}」。這題只要寫一個字母（{how}）就好。"
                    continue
                r.ok = norm_answer(letter, kind, home) in accepted
            else:
                r.ok = norm_answer(given, kind, home) in accepted
            if not r.ok:
                r.detail = f"你寫「{given.strip()}」，不對。" + (f"\n  提示：{q['hint']}" if q.get("hint") else "")
            elif q.get("explain"):
                r.note = q["explain"]


# ---------------- 0-5 環境 ----------------

PACKAGE_REDO = (
    "重來的方法：在帳本資料夾裡打 rm -r src 和 rm pyproject.toml，"
    "再打 uv init --no-package --vcs none --python 3.13（它會建出 main.py）。"
)


def is_package_layout(ledger: Path | None) -> bool:
    if ledger is None:
        return False
    path = ledger / "pyproject.toml"
    try:
        return "build-system" in tomllib.loads(read_student_text(path))
    except (NotReady, tomllib.TOMLDecodeError, OSError):
        return False


class UvProjectCheck(Check):
    def run(self, results):
        r = results[0]
        path = self.ctx.student("pyproject.toml")
        if not path.is_file():
            r.detail = "帳本裡找不到 pyproject.toml，所以還不是 uv 專案。\n  在帳本資料夾裡打：uv init --no-package --vcs none --python 3.13"
            return
        try:
            data = tomllib.loads(read_student_text(path))
        except tomllib.TOMLDecodeError as exc:
            r.detail = f"pyproject.toml 壞掉了，讀不懂：{exc}\n  最簡單的修法：刪掉它，再打一次 uv init --no-package --vcs none --python 3.13"
            return
        project = data.get("project")
        if not isinstance(project, dict) or not project.get("name"):
            r.detail = "pyproject.toml 裡沒有 [project] 這一段。刪掉它，再打一次 uv init --no-package --vcs none --python 3.13"
            return
        r.ok = True
        if "build-system" in data:
            r.note = "看起來是用「套件結構」建的（少打了 --no-package），這門課要用最簡單的結構。"
            if not self.ctx.student("main.py").is_file():
                r.note += "這種結構不會建 main.py。" + PACKAGE_REDO


class PythonPinCheck(Check):
    def run(self, results):
        r = results[0]
        want = self.spec.get("version", "3.13")
        path = self.ctx.student(".python-version")
        if not path.is_file():
            r.detail = f"帳本裡找不到 .python-version，代表還沒釘住 Python 版本。\n  在帳本資料夾裡打：uv python pin {want}"
            return
        got = read_student_text(path).strip().splitlines()[0:1]
        got = got[0].strip() if got else ""
        r.ok = got == want or got.startswith(want + ".")
        if not r.ok:
            r.detail = f"帳本釘的是「{got or '（空白）'}」，這門課要 {want}。\n  在帳本資料夾裡打：uv python pin {want}"


SYSTEM_PLACES = (
    "/System/",
    "/Library/Developer/CommandLineTools",
    "/Applications/Xcode",
)


def is_system_python(base_prefix: str) -> bool:
    base = base_prefix.replace("\\", "/")
    if base in ("/usr", "/usr/") or (base.startswith("/usr/") and not base.startswith("/usr/local")):
        return True
    if "WindowsApps" in base:
        return True
    return any(base.startswith(p) for p in SYSTEM_PLACES)


class UvPythonCheck(Check):
    def run(self, results):
        r = results[0]
        want = self.spec.get("version", "3.13")
        info = self.ctx.env.probe()
        version = ".".join(str(x) for x in info["version"][:2])
        problems = []
        if version != want:
            problems.append(f"帳本現在用的是 Python {version}，這門課要 {want}。打：uv python pin {want}，再跑一次")
        ledger = self.ctx.ledger
        venv = Path(info["prefix"]).resolve()
        if ledger is not None and venv != (ledger / ".venv").resolve():
            problems.append(f"這個 Python 不在帳本的 .venv 裡（它在 {info['prefix']}）。在帳本資料夾裡打一次 uv run main.py 試試看")
        if is_system_python(info["base_prefix"]):
            problems.append(f"這是電腦內建的系統 Python（{info['base_prefix']}）。不要用它，改用 uv 裝的 Python：uv python pin {want}")
        r.ok = not problems
        r.detail = first_problem(problems)
        if r.ok:
            r.note = f"Python {version}，在帳本的 .venv 裡（底下是 {info['base_prefix']}）"


# ---------------- run ----------------

def crash_story(p: Proc, stdin: str, given_label: str = "這題") -> str:
    """學員程式當掉時，給新手看的第一句話。"""
    err = p.stderr
    if "EOFError" in err:
        return (f"你的程式要的輸入比{given_label}給的多（{given_label}只給了：{show_stdin(stdin)}）。"
                "檢查是不是多寫了一個 input()。")
    if "SyntaxError" in err and ("Non-UTF-8" in err or "utf-8" in err.lower() and "decode" in err.lower()):
        return f"這支程式不是用 UTF-8 存的，Python 讀不懂。{ENCODING_HELP}"
    return "程式當掉了。錯誤訊息最後幾行：\n" + tail(err)


class RunCheck(Check):
    def missing_text(self, rel: str) -> str:
        hint = self.spec.get("missing_hint")
        if self.spec.get("package_hint") and is_package_layout(self.ctx.ledger):
            hint = "你的帳本是用「套件結構」建的（少打了 --no-package），這種結構不會建 main.py。" + PACKAGE_REDO
        return self.ctx.missing(rel, hint)

    def run(self, results):
        r = results[0]
        rel = self.spec["file"]
        path = self.ctx.student(rel)
        if not path.is_file():
            r.detail = self.missing_text(rel)
            return
        stdin = self.spec.get("stdin", "")
        feed = f"餵給它的輸入：{show_stdin(stdin)}\n  " if stdin else ""
        hint = self.spec.get("hint")
        hint_text = f"\n  提示：{hint}" if hint else ""
        if str(path) in self.ctx.stuck:
            r.detail = f"同一支程式剛剛就{self.ctx.stuck[str(path)]}，這題先不再等一次。先修好那個問題。"
            return
        p = self.ctx.env.run_file(path, stdin=stdin)
        if p.timed_out:
            self.ctx.stuck[str(path)] = f"跑了 {self.ctx.env.timeout:.0f} 秒還沒結束"
            r.detail = feed + f"跑了 {self.ctx.env.timeout:.0f} 秒還沒結束，被停下來了：可能有無窮迴圈。"
            return
        if p.overflow:
            self.ctx.stuck[str(path)] = "印了太多東西被停下來"
            r.detail = feed + "你的程式印了太多東西，被停下來了：可能是迴圈沒停下來。"
            return
        if p.returncode != 0:
            r.detail = feed + crash_story(p, stdin) + (hint_text if self.spec.get("hint_on_crash", True) else "")
            return
        got = output_lines(p.stdout)
        joined = "\n".join(got)
        shown = "\n".join("    " + ln.rstrip() for ln in p.stdout.splitlines() if ln.strip()) or "    （什麼都沒印）"
        problems = []
        if "expect_exact" in self.spec:
            want = output_lines("\n".join(self.spec["expect_exact"]) if isinstance(self.spec["expect_exact"], list) else self.spec["expect_exact"])
            if got != want:
                problems.append("印出來的跟應該的不一樣。\n  應該是：\n" + "\n".join("    " + w for w in want) + "\n  你的印出：\n" + shown)
        for pattern in self.spec.get("expect_regex", []):
            if not re.search(pattern, joined, re.MULTILINE):
                problems.append("沒有看到應該要印的字。\n  你的印出：\n" + shown)
        for word in self.spec.get("expect_contains", []):
            if norm_line(word) not in joined:
                problems.append(f"應該要看到{show(word)}，可是沒有。\n  你的印出：\n" + shown)
        for word in self.spec.get("expect_not_contains", []):
            if norm_line(word) in joined:
                problems.append(f"不應該出現{show(word)}，可是出現了。\n  你的印出：\n" + shown)
        r.ok = not problems
        if problems:
            r.detail = feed + problems[0] + hint_text


# ---------------- call ----------------

class CallCheck(Check):
    def plan(self):
        s = self.spec
        desc = s.get("desc") or f"{s['func']}({args_text(s.get('args', []))}) 應該是{show(s['expect'])}"
        return [self.stub(None, desc)]

    def _batch(self) -> dict:
        s = self.spec
        key = (s["file"], s["module"], s["func"])
        if key in self.ctx._call_cache:
            return self.ctx._call_cache[key]
        specs = [c for c in self.ctx.lesson.checks if c["type"] == "call" and (c["file"], c["module"], c["func"]) == key]
        path = self.ctx.student(s["file"])
        if not path.is_file():
            data = {"missing": True}
        else:
            reply = self.ctx.env.runner({
                "op": "call",
                "file": str(path),
                "module": s["module"],
                "func": s["func"],
                "cases": [{"args": c.get("args", []), "expect": c["expect"]} for c in specs],
            })
            data = {"reply": reply, "ids": [c["id"] for c in specs]}
        self.ctx._call_cache[key] = data
        return data

    def run(self, results):
        r = results[0]
        s = self.spec
        data = self._batch()
        name = Path(s["file"]).name
        if data.get("missing"):
            r.detail = self.ctx.missing(s["file"])
            return
        reply = data["reply"]
        err = reply.get("load_error")
        if err:
            kind = err["kind"]
            if kind == "syntax":
                r.detail = f"你的 {name} 第 {err['line']} 行有語法錯誤（{err['msg']}），程式根本跑不起來。先讀那一行。"
            elif kind == "encoding":
                r.detail = f"你的 {name} 不是用 UTF-8 存的，Python 讀不懂。{ENCODING_HELP}"
            elif kind == "missing":
                r.detail = f"你的 {name} 裡找不到 {s['func']}。def 那一行的名字不要改。"
            elif kind == "input":
                r.detail = f"你的 {name} 一載入就在等 input()。這個檔案只要寫函式，不要放 input()。"
            else:
                where = f"第 {err['line']} 行" if err.get("line") else "載入時"
                r.detail = f"你的 {name} {where}就當掉了：{err['msg']}"
            return
        case = reply["cases"][data["ids"].index(s["id"])]
        r.ok = bool(case.get("ok"))
        if r.ok:
            return
        call = f"{s['func']}({args_text(s.get('args', []))})"
        if "error" in case:
            r.detail = f"{call} 應該回傳{show(s['expect'])}，可是你的程式當掉了：{case['error']}"
        else:
            r.detail = f"{call} 應該回傳{show(s['expect'])}，你的回傳{show(case.get('got'))}"
            if case.get("got") is None:
                r.detail += "\n  回傳 None，常常是用了 print，而不是 return。"
        if s.get("hint"):
            r.detail += f"\n  提示：{s['hint']}"


# ---------------- chaff（wheat/chaff） ----------------

@dataclass
class StudentCheck:
    line: int
    text: str
    must: bool = True  # path_checks 用：True＝要有，False＝不該有
    stmt: ast.AST | None = None


@dataclass
class Mark:
    line: int
    kind: str
    text: str
    stmt: ast.AST


@dataclass
class Parsed:
    checks: list[StudentCheck]
    marks: list[Mark]
    problem: str | None
    unfinished: int
    notes: list[str]


NOT_RUN = {"status": "error", "error": "沒有跑到（前面卡住了）", "not_run": True}


def _comments(source: str) -> dict[int, str]:
    out: dict[int, str] = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT:
                out[tok.start[0]] = out.get(tok.start[0], "") + tok.string
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return out


def _mark_in(comment: str) -> str | None:
    """行尾註解「開頭就是」已知會當掉／需求有問題，才算特殊作答（只是提到不算）。"""
    flat = "".join(unicodedata.normalize("NFKC", comment).split()).lstrip("#")
    for kind in SPECIAL_MARKS:
        if flat.startswith(kind):
            return kind
    return None


def split_label(text: str) -> tuple[str, str] | None:
    """「標籤：值」拆成兩段。標籤去掉所有空白，全形半形冒號都認得。"""
    t = unicodedata.normalize("NFKC", text)  # 全形冒號會變成半形
    if ":" not in t:
        return None
    label, value = t.split(":", 1)
    return "".join(label.split()), "".join(value.split())


class ChaffCheck(Check):
    def __init__(self, spec, ctx):
        super().__init__(spec, ctx)
        self.mode = spec["mode"]
        info = json.loads(ctx.course(spec["mutants"]).read_text(encoding="utf-8"))
        self.mutants = info["mutants"]
        self.mutant_dir = ctx.course(spec["mutants"]).parent
        self.min = spec.get("min_checks", 1)
        self._parsed: Parsed | None = None
        self.ref_labels: list[str] = []
        self.has_import = True

    # ----- 讀學員的檢查 -----
    def parse(self) -> Parsed:
        if self._parsed is not None:
            return self._parsed
        rel = self.spec["student_file"]
        checks: list[StudentCheck] = []
        marks: list[Mark] = []
        notes: list[str] = []
        problem = None
        unfinished = 0
        try:
            path = self.ctx.student(rel)
        except NotReady:
            path = None
        source = None
        if path is None or not path.is_file():
            problem = self.ctx.missing(rel)
        else:
            try:
                source = read_student_text(path)
            except NotReady as exc:
                problem = str(exc)
        if source is not None:
            lines = source.splitlines()
            module = self.spec.get("module")
            if module:
                self.has_import = bool(re.search(rf"^\s*(from\s+{re.escape(module)}\s+import|import\s+{re.escape(module)}\b)",
                                                 source, re.MULTILINE))
            if self.mode == "assert":
                try:
                    tree = ast.parse(source)
                except SyntaxError as exc:
                    problem = f"你的 {Path(rel).name} 第 {exc.lineno} 行有語法錯誤（{exc.msg}），先修好它。"
                    bad = lines[exc.lineno - 1] if exc.lineno and exc.lineno <= len(lines) else ""
                    if "assert" in bad and re.search(r"(?<![=!<>])=(?!=)", bad):
                        problem += "\n  比較兩個東西一不一樣，要用兩個等號 ==（一個等號是「放進去」）。"
                    tree = None
                if tree is not None:
                    comments = _comments(source)
                    for stmt in tree.body:
                        if not isinstance(stmt, ast.Assert):
                            inner = [n for n in ast.walk(stmt) if isinstance(n, ast.Assert)]
                            if inner:
                                notes.append(
                                    f"第 {inner[0].lineno} 行的 assert 寫在 for、if 或 def 裡面，不算在檢查裡；"
                                    "assert 要寫在最外層（最左邊不空格）才會算。"
                                )
                            continue
                        text = " ".join(x.strip() for x in lines[stmt.lineno - 1: stmt.end_lineno])
                        kind = None
                        for ln in range(stmt.lineno, (stmt.end_lineno or stmt.lineno) + 1):
                            kind = kind or _mark_in(comments.get(ln, ""))
                        if kind:
                            marks.append(Mark(stmt.lineno, kind, text, stmt))
                        else:
                            checks.append(StudentCheck(stmt.lineno, text, stmt=stmt))
            else:
                for i, raw in enumerate(lines, start=1):
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "？" in line or "?" in line:
                        unfinished += 1
                        continue
                    if self.mode == "path_checks":
                        line = line.replace("\\", "/")
                        flat = unicodedata.normalize("NFKC", line)
                        if flat.startswith("沒有"):
                            checks.append(StudentCheck(i, line, must=False))
                            continue
                    checks.append(StudentCheck(i, line))
        self._parsed = Parsed(checks, marks, problem, unfinished, notes)
        return self._parsed

    def plan(self):
        parsed = self.parse()
        out = [
            self.stub("count", f"至少寫 {self.min} 條檢查"),
            self.stub("wheat", "你的檢查在正確版上要全部成立"),
        ]
        for i, _m in enumerate(self.mutants, start=1):
            out.append(self.stub(f"m{i}", f"抓到第 {i} 個壞版本"))
        for mk in parsed.marks:
            stub = self.stub(f"s{mk.line}", f"第 {mk.line} 行標了「{mk.kind}」")
            stub.special = True
            out.append(stub)
        return out

    # ----- 每個版本各跑一次（各自一個程序） -----
    def impls(self) -> dict[str, Path]:
        out = {"reference": self.ctx.course(self.spec["reference"])}
        for i, m in enumerate(self.mutants, start=1):
            out[f"m{i}"] = self.mutant_dir / m["file"]
        return out

    def version_timeout(self) -> float:
        return min(self.ctx.env.timeout, float(self.spec.get("timeout", 10)))

    def run_assert_version(self, impl: Path, lines: list[int]) -> dict[int, dict]:
        """跑一個版本，回傳 {行號: 結果}。卡住或印太多被收掉的，也照進度算出每一行的結果。"""
        timeout = self.version_timeout()
        reply = self.ctx.env.runner_raw({
            "op": "asserts",
            "checks_file": str(self.ctx.student(self.spec["student_file"])),
            "module": self.spec["module"],
            "impl": str(impl),
        }, timeout=timeout)
        data = reply.result
        if data is not None:
            if "runner_error" in data:
                raise RunnerTrouble("檢查程式出錯了：" + data["runner_error"])
            if "syntax" in data:
                raise RunnerTrouble(f"第 {data['syntax']['line']} 行有語法錯誤（{data['syntax']['msg']}）")
            if data.get("encoding"):
                raise NotReady(f"{Path(self.spec['student_file']).name} 不是用 UTF-8 存的。{ENCODING_HELP}")
            return {a["line"]: a for a in data["asserts"]}
        p = reply.proc
        if p.timed_out:
            why = f"跑了 {timeout:.0f} 秒還沒結束（可能卡在無窮迴圈）"
        elif p.overflow:
            why = "印了太多東西被停下來（可能是迴圈沒停下來）"
        else:
            why = "整支程式直接結束了（可能呼叫了 exit）：" + (tail(p.stderr, 2).strip() or "沒有錯誤訊息")
        done: dict[int, dict] = {}
        current = None
        for kind, rest in reply.events:
            if kind == "start":
                current = rest
            elif kind == "done":
                try:
                    rec = json.loads(rest)
                except ValueError:
                    continue
                done[rec["line"]] = rec
                current = None
        out: dict[int, dict] = {}
        blocked = None
        if current == "load":
            blocked = f"載入時就{why}"
        elif current and current.startswith("stmt "):
            blocked = f"第 {current.split()[1]} 行就{why}"
        stuck_line = int(current.split()[1]) if current and current.startswith("assert ") else None
        for ln in lines:
            if ln in done:
                out[ln] = done[ln]
            elif blocked:
                out[ln] = {"line": ln, "status": "error", "error": blocked, "stuck": True}
            elif ln == stuck_line:
                out[ln] = {"line": ln, "status": "error", "error": why, "stuck": True}
            elif stuck_line is not None and ln > stuck_line:
                out[ln] = dict(NOT_RUN, line=ln)
            else:
                out[ln] = {"line": ln, "status": "error", "error": why, "stuck": True}
        return out

    def statuses(self, checks: list[StudentCheck], marks: list[Mark]) -> tuple[dict[str, list[dict]], dict[int, dict]]:
        """回傳（每個版本每一條檢查的結果, 正確版上每一條特殊作答的結果）。"""
        impls = self.impls()
        out: dict[str, list[dict]] = {}
        mark_status: dict[int, dict] = {}
        if self.mode == "assert":
            lines = sorted([c.line for c in checks] + [m.line for m in marks])
            for name, path in impls.items():
                by_line = self.run_assert_version(path, lines)
                out[name] = [by_line.get(c.line, dict(NOT_RUN)) for c in checks]
                if name == "reference":
                    mark_status = {m.line: by_line.get(m.line, dict(NOT_RUN)) for m in marks}
        elif self.mode == "expected_output":
            pairs = self.spec.get("line_format") == "label_value"
            for name, path in impls.items():
                p = self.ctx.env.run_file(path, timeout=self.version_timeout())
                printed = output_lines(p.stdout)
                if name == "reference":  # 只留冒號前面的字（給學員看格式），不留答案
                    self.ref_labels = [x.split(":", 1)[0].strip() for x in printed if ":" in x]
                crashed = p.returncode != 0 or p.stopped
                rows = []
                for c in checks:
                    if crashed:
                        rows.append({"status": "error", "error": "這個版本當掉了"})
                    elif pairs:
                        rows.append(self.match_pair(c.text, printed))
                    else:
                        rows.append({"status": "pass" if norm_line(c.text) in printed else "fail"})
                out[name] = rows
        elif self.mode == "path_checks":
            sc = json.loads(self.ctx.course(self.spec["scenario"]).read_text(encoding="utf-8"))
            for name, path in impls.items():
                res = vshell.run(path.read_text(encoding="utf-8"), sc["home"], sc["cwd"], sc.get("start", []))
                rows = []
                for c in checks:
                    target = c.text[2:].strip() if not c.must else c.text
                    there = vshell.exists(res, sc["cwd"], target)
                    rows.append({"status": "pass" if there == c.must else "fail"})
                out[name] = rows
        else:
            raise RunnerTrouble(f"不認得的模式：{self.mode}")
        return out, mark_status

    @staticmethod
    def match_pair(text: str, printed: list[str]) -> dict:
        mine = split_label(text)
        if mine is None:
            return {"status": "fail", "why": "colon"}
        table = {}
        for line in printed:
            sp = split_label(line)
            if sp:
                table.setdefault(sp[0], sp[1])
        if mine[0] not in table:
            return {"status": "fail", "why": "label"}
        return {"status": "pass" if table[mine[0]] == mine[1] else "fail", "why": "value"}

    def describe_ref_failure(self, c: StudentCheck, st: dict) -> str:
        if self.mode == "assert":
            msg = f"第 {c.line} 行：{c.text}\n  "
            err = st.get("error") or ""
            if st.get("not_run"):
                return msg + "前面卡住了，這一行沒有跑到。"
            if st.get("stuck"):
                return msg + f"在正確版上{err}。如果你的檢查裡有迴圈，看看它停不停得下來。"
            if st.get("status") == "error":
                if "NameError" in err and not self.has_import:
                    return msg + (f"程式不認得這個名字（{err}）。"
                                  f"最上面那行 from {self.spec.get('module')} import … 要留著，不要刪掉。")
                return (msg + f"在正確版上就不成立，而且會當掉（{err}）。\n"
                        "  如果你本來就是要測「正確版也會當掉」的情況，在這行最後加上「# 已知會當掉」。")
            msg += "在正確版上就不成立"
            if st.get("got") is not None:
                msg += f"（正確版算出來是{show(st['got'])}）"
            return msg + "。\n  正確版不會錯，所以是這條檢查要改；如果你覺得是需求沒講清楚，在行尾加上「# 需求有問題」。"
        if self.mode == "expected_output":
            if st.get("status") == "error":
                return f"第 {c.line} 行「{c.text}」：正確版在你的帳本裡跑不起來，先確定 0-5 前面幾題都過了。"
            if self.spec.get("line_format") == "label_value":
                labels = "「" + "」「".join(self.ref_labels) + "」" if self.ref_labels else "原本的寫法"
                why = st.get("why")
                if why == "colon":
                    return f"第 {c.line} 行「{c.text}」少了冒號。照原本的格式「開頭：答案」寫，只改「？」那裡。"
                if why == "label":
                    return (f"第 {c.line} 行「{c.text}」：冒號前面的字被改到了，只要改「？」就好。\n"
                            f"  冒號前面照原本的寫：{labels}。")
                mine = split_label(c.text)
                hints = {"".join(unicodedata.normalize("NFKC", k).split()): v
                         for k, v in self.spec.get("value_hints", {}).items()}
                hint = hints.get(mine[0] if mine else "", "再想想看：在你的帳本裡用 uv run 跑，會是什麼情況？")
                return f"第 {c.line} 行「{c.text}」：正確版在你的帳本裡印的不是這個答案。\n  提示：{hint}"
            return f"第 {c.line} 行「{c.text}」：正確版沒有印出這一行。"
        target = c.text[2:].strip() if not c.must else c.text
        return f"第 {c.line} 行「{c.text}」：正確版跑完之後，{target} {'並不存在' if c.must else '其實還在'}。"

    def run(self, results):
        parsed = self.parse()
        checks, marks, problem, unfinished = parsed.checks, parsed.marks, parsed.problem, parsed.unfinished
        by_id = {r.id.rsplit("-", 1)[-1]: r for r in results}
        count_r, wheat_r = by_id["count"], by_id["wheat"]
        mutant_rs = [by_id[f"m{i}"] for i in range(1, len(self.mutants) + 1)]
        if problem:
            for r in results:
                r.detail = problem
            return
        self.ctx.summaries.extend(parsed.notes)

        n = len(checks)
        count_r.ok = n >= self.min
        if not count_r.ok:
            extra = f"（還有 {unfinished} 行有「？」沒填完）" if unfinished else ""
            marked = "；行尾標了特殊作答的不算在裡面" if marks else ""
            count_r.detail = f"你寫了 {n} 條檢查，這課要至少 {self.min} 條{extra}{marked}。"
        reveal = count_r.ok  # 寫滿最少條數以前，先不講溜過去的是哪一種錯

        mark_status: dict[int, dict] = {}
        if n or (marks and self.mode == "assert"):
            st, mark_status = self.statuses(checks, marks)
        if n:
            ref = st["reference"]
            bad = [(c, s) for c, s in zip(checks, ref) if s.get("status") != "pass"]
            wheat_r.ok = not bad
            if bad:
                wheat_r.detail = self.describe_ref_failure(*bad[0]) + (f"\n  （一共有 {len(bad)} 條在正確版上不成立）" if len(bad) > 1 else "")
            valid = [i for i, s in enumerate(ref) if s.get("status") == "pass"]
            slipped = []
            for k, (m, r) in enumerate(zip(self.mutants, mutant_rs), start=1):
                rows = st[f"m{k}"]
                catchers = [i for i in valid if rows[i].get("status") != "pass"]
                r.ok = bool(catchers)
                if r.ok:
                    first = catchers[0]
                    r.note = f"被第 {checks[first].line} 行抓到"
                    if rows[first].get("stuck"):
                        r.note += "（這個壞版本卡住了、跑不完，你的檢查抓到它）"
                elif not valid:
                    r.detail = "你的檢查在正確版上還沒有一條成立，先修好正確版那一題。"
                    slipped.append(m["hint"])
                else:
                    r.detail = f"溜過去了：{m['hint']}" if reveal else f"溜過去了。（先寫滿 {self.min} 條檢查，再告訴你溜過去的是哪一種錯）"
                    slipped.append(m["hint"])
            caught = len(self.mutants) - len(slipped)
            if not slipped:
                self.ctx.summaries.append(f"你的檢查把 {len(self.mutants)} 個壞版本全部抓到了。")
            elif reveal:
                # 每行壓在 68 欄內（VHS 錄影 70 欄、Terminal.app 預設 80 欄都不折行）：提示一條一行
                self.ctx.summaries.append(f"你的檢查抓到 {caught} 個壞版本，還有 {len(slipped)} 個溜過去：")
                self.ctx.summaries.extend(f"  ・{h}" for h in slipped)
            else:
                self.ctx.summaries.append(
                    f"你的檢查抓到 {caught} 個壞版本，還有 {len(slipped)} 個溜過去（先寫滿 {self.min} 條檢查，再告訴你是哪幾種）。"
                )
        else:
            wheat_r.detail = "還沒有任何檢查。" + (f"（有 {unfinished} 行的「？」還沒填）" if unfinished else "")
            for r in mutant_rs:
                r.detail = "還沒有任何檢查，所以壞版本都溜過去了。"

        if marks:
            key = json.loads(self.ctx.course(self.spec["special"]).read_text(encoding="utf-8")) if self.spec.get("special") else {"rules": []}
            for mk in marks:
                r = by_id[f"s{mk.line}"]
                r.ok, r.detail, r.note = judge_mark(mk, key, mark_status.get(mk.line, {}))


def _rule_matches(rule: dict, args: list) -> bool:
    idx = rule.get("arg", 0)
    if idx >= len(args):
        return False
    v = args[idx]
    is_number = isinstance(v, (int, float)) and not isinstance(v, bool)
    kind = rule.get("is")
    if kind:
        ok = {
            "str": isinstance(v, str),
            "number": is_number,
            "int": isinstance(v, int) and not isinstance(v, bool),
            "float": isinstance(v, float),
            "none": v is None,
            "list": isinstance(v, list),
            "bool": isinstance(v, bool),
        }.get(kind, False)
        if not ok:
            return False
    op = rule.get("op")
    if op:
        if not is_number:
            return False
        value = rule["value"]
        return {
            "<": v < value, "<=": v <= value, ">": v > value, ">=": v >= value, "==": v == value, "!=": v != value,
        }[op]
    return True


def judge_mark(mk: Mark, key: dict, ref: dict) -> tuple[bool, str, str]:
    """對特殊作答。「已知會當掉」看正確版真的跑這一行會不會當掉；「需求有問題」照 special.json 的規則。"""
    func = key.get("func")
    calls = [
        n for n in ast.walk(mk.stmt.test)
        if isinstance(n, ast.Call) and (getattr(n.func, "id", None) == func or getattr(n.func, "attr", None) == func)
    ]
    if func and not calls:
        return False, f"第 {mk.line} 行標了「{mk.kind}」，可是這行沒有呼叫 {func}()。", ""
    args = None
    if calls:
        try:
            args = [ast.literal_eval(a) for a in calls[0].args]
        except ValueError:
            args = None
    call = f"{func}({args_text(args)})" if args is not None else (ast.unparse(calls[0]) if calls else "這一行")
    status = ref.get("status")
    err = ref.get("error", "")
    if ref.get("skipped") or ref.get("not_run"):
        return False, f"第 {mk.line} 行標了「{mk.kind}」，可是前面的程式先出錯了，這一行沒有跑到。先修好前面的錯。", ""
    crashed = status == "error" and not ref.get("stuck")
    rules = key.get("rules", [])
    matching = [r for r in rules if args is not None and _rule_matches(r, args)]

    if mk.kind == "已知會當掉":
        if crashed:
            explain = next((r["explain"] for r in matching if r["kind"] == "已知會當掉"), "")
            return True, "", f"{call}：正確版跑這一行真的會當掉（{err}）。" + (explain and f"{explain}")
        if ref.get("stuck"):
            return False, f"第 {mk.line} 行標了「已知會當掉」，可是正確版跑這一行是卡住（{err}），不是當掉。", ""
        if any(r["kind"] == "需求有問題" for r in matching):
            return False, f"第 {mk.line} 行標了「已知會當掉」，方向對了一半：正確版跑 {call} 並不會當掉，這比較像「需求有問題」。", ""
        how = "這條檢查成立" if status == "pass" else "這條檢查不成立，可是沒有當掉"
        return False, (f"第 {mk.line} 行標了「已知會當掉」，可是正確版跑 {call} 並不會當掉（{how}）。"
                       "\n  把標記拿掉，當成一般的檢查就好。"), ""

    # 需求有問題
    if crashed:
        return False, (f"第 {mk.line} 行標了「需求有問題」，方向對了一半：正確版跑 {call} 會當掉（{err}），"
                       "這比較像「已知會當掉」。"), ""
    if args is None and calls:
        return False, f"第 {mk.line} 行標了「需求有問題」，可是看不出來你傳了什麼。請直接寫數字或文字，不要用變數。", ""
    for rule in matching:
        if rule["kind"] == "需求有問題":
            return True, "", f"{call}：{rule['explain']}"
    return False, (
        f"第 {mk.line} 行標了「需求有問題」，可是 {call} 的需求講得很清楚。"
        "\n  把標記拿掉，當成一般的檢查就好。"
    ), ""


# ---------------- script_match ----------------

class ScriptMatchCheck(Check):
    def run(self, results):
        r = results[0]
        rel = self.spec["student_file"]
        path = self.ctx.student(rel)
        if not path.is_file():
            r.detail = self.ctx.missing(rel)
            return
        if has_crlf(path):
            r.detail = CRLF_HELP
            return
        sc = json.loads(self.ctx.course(self.spec["scenario"]).read_text(encoding="utf-8"))
        mine = vshell.run(read_student_text(path), sc["home"], sc["cwd"], sc.get("start", []))
        ref = vshell.run(self.ctx.course(self.spec["reference"]).read_text(encoding="utf-8"), sc["home"], sc["cwd"], sc.get("start", []))
        extra, lost = vshell.diff(mine, ref, sc["cwd"])
        problems = [f"你的版本第 {ln} 行{msg}" if msg.startswith("有模擬器") else f"你的版本第 {ln} 行會出錯：{msg}"
                    for ln, msg in mine.errors]
        problems += [f"跑你的版本，{p} 會不見（被刪掉或搬走）" for p in lost]
        problems += [f"跑你的版本，會多出 {p}" for p in extra]
        r.ok = not problems
        r.detail = first_problem(problems)
        if r.ok:
            r.note = "在假的資料夾裡模擬過了，跟安全版跑出來一樣。"


# ---------------- git_commits ----------------

class GitCheck(Check):
    def run(self, results):
        r = results[0]
        ledger = self.ctx.ledger
        if ledger is None:
            raise NotReady("還不知道你的帳本在哪裡。先打：uv run check.py setup ~/code/ledger")
        if not (ledger / ".git").exists():
            r.detail = ("帳本還不是 git 存放庫（找不到 .git 資料夾）。照 0-7：用 VS Code 打開帳本，"
                        "在「原始碼控制」面板按「初始化存放庫」，再按存檔點。")
            return
        git = shutil.which("git")
        if not git:
            r.detail = "找不到 git 這個指令。Mac 打 xcode-select --install（0-5 做過）；Windows 裝 Git for Windows。"
            return
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", LC_ALL="C")
        p = procs.run([git, "rev-list", "--count", "HEAD"], cwd=ledger, env=env, timeout=30)
        count = int(p.stdout.strip()) if p.returncode == 0 and p.stdout.strip().isdecimal() else 0
        need = int(self.spec.get("min", 2))
        if count < need:
            r.detail = (f"帳本現在有 {count} 個存檔點，這一關要至少 {need} 個。"
                        "在 VS Code 的「原始碼控制」面板寫一句說明、按存檔點（commit）。")
            return
        for rel in self.spec.get("committed", []):
            p = procs.run([git, "status", "--porcelain", "--", rel], cwd=ledger, env=env, timeout=30)
            if p.returncode == 0 and p.stdout.strip():
                r.detail = f"{rel} 改過之後還沒按存檔點。在「原始碼控制」面板把它存起來（commit）。"
                return
        r.ok = True
        r.note = f"帳本有 {count} 個存檔點"


CHECKERS = {
    "tree": TreeCheck,
    "answers": AnswersCheck,
    "uv_project": UvProjectCheck,
    "python_pin": PythonPinCheck,
    "uv_python": UvPythonCheck,
    "run": RunCheck,
    "call": CallCheck,
    "chaff": ChaffCheck,
    "script_match": ScriptMatchCheck,
    "git_commits": GitCheck,
}


# ====================================================================
# 對外的入口
# ====================================================================

def build(lesson: Lesson, ledger: Path | None, env: Env | None = None,
          overrides: dict[str, Path] | None = None, only: list[dict] | None = None):
    env = env or Env(ledger)
    ctx = Ctx(lesson=lesson, ledger=ledger, env=env, overrides=overrides or {})
    specs = only if only is not None else lesson.checks
    checkers = [CHECKERS[s["type"]](s, ctx) for s in specs]
    return ctx, checkers


def plan(lesson: Lesson, ledger: Path | None) -> list[Result]:
    _ctx, checkers = build(lesson, ledger)
    out = []
    for ch in checkers:
        out.extend(ch.plan())
    return out


def evaluate(lesson: Lesson, ledger: Path | None, env: Env | None = None,
             overrides: dict[str, Path] | None = None, only: list[dict] | None = None) -> Outcome:
    ctx, checkers = build(lesson, ledger, env, overrides, only)
    results: list[Result] = []
    for ch in checkers:
        stubs = ch.plan()
        try:
            ch.run(stubs)
        except (NotReady, RunnerTrouble) as exc:
            for r in stubs:
                r.ok = False
                r.detail = str(exc)
        except UnicodeError:
            for r in stubs:
                r.ok = False
                r.detail = f"有一個檔案不是用 UTF-8 存的，check.py 讀不懂。{ENCODING_HELP}"
        except OSError as exc:
            for r in stubs:
                r.ok = False
                r.detail = f"讀寫檔案的時候出了問題：{exc.strerror or exc}（{getattr(exc, 'filename', '') or ''}）"
        results.extend(stubs)
    return Outcome(results=results, summaries=ctx.summaries)
