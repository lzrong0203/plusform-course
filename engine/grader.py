"""判分引擎：讀每課的 tests/checks.json，一項一項檢查。

check.py（學員端）和 tools/validate_lesson.py（老師端）共用這一份。
只用 Python 標準庫；絕不呼叫任何 AI 或網路服務（帳本的 uv 也加 --offline，不讓它連網）。

檢查的種類（checks.json 裡每一項的 "type"）：
  tree          帳本裡應該有／不該有哪些資料夾和檔案
  answers       對答：學員在「答：」後面寫的答案，對照 answers/ 的固定答案（題目自己的 choices 優先，1-C1 起）
  uv_project    帳本是 uv 專案（有 pyproject.toml）
  python_pin    帳本把 Python 釘在指定版本（.python-version）
  uv_python     帳本用的是自己 .venv 裡的 Python，不是系統 Python
  run           在帳本的環境裡跑學員的程式（stdin 由這裡餵），比對印出來的字；swap＝先把一行換掉再跑（1-C1 第三部分：
                金額換了也要算得對）；當掉時 Result.data["error"] 記錯誤種類（1-C1 矯正包用）
  call          呼叫學員寫的函式，比對回傳值
  chaff         wheat/chaff：學員寫的檢查要在正確版全過、在每個壞版本至少錯一條
  script_match  學員改過的腳本，在假的資料夾裡跑起來要跟安全版一樣
  git_commits   帳本是 git 存放庫，而且至少有幾個存檔點（commit）
  parsons       拼圖（Parsons，1-11 起）：把打亂的程式行排回去、自己縮排；行都要是題目給的（不能改字、多寫、少寫），排好跑出來要跟範例一樣

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
import tempfile
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
    # 檢核站的平行卷（1-C1 起）：1-C1B、1-c1b、1-C1-B 都當成 1-C1B（卷 B 放在 lessons/1-C1/B/，見 load_lesson）
    m = re.fullmatch(r"(\d+)-[cC](\d+)[-_ ]?([bB])", text)
    if m:
        return f"{int(m.group(1))}-C{m.group(2)}B"
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


PAPER_ID = re.compile(r"(\d+-C\d+)([B-Z])")


def paper_folder(lesson_id: str, root: Path = COURSE_ROOT) -> Path | None:
    """檢核站的平行卷（1-C1 起）：1-C1B 放在 lessons/1-C1/B/（不在課表裡，回顧題、課表順序都照原本的 1-C1）。"""
    m = PAPER_ID.fullmatch(lesson_id)
    if not m:
        return None
    folder = root / "lessons" / m.group(1) / m.group(2)
    return folder if (folder / "lesson.json").is_file() else None


def load_lesson(lesson_id: str, root: Path = COURSE_ROOT) -> Lesson:
    folder = root / "lessons" / lesson_id
    meta_path = folder / "lesson.json"
    if not meta_path.is_file():
        folder = paper_folder(lesson_id, root) or folder
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
    "parsons": "官方測試",
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
        for i, (r, q) in enumerate(zip(results, key["questions"]), start=1):
            # 1-C1 起：題目自己寫了 choices 就用它（同一個作答檔裡有的寫數字、有的選 A／B／C）；沒寫照舊用整份的
            choices = q.get("choices") or key.get("choices")
            how = (or_list(sorted(choices)) if q.get("choices") else None) or key.get("how") or (or_list(sorted(choices)) if choices else "你的答案")
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


ERROR_LINE = re.compile(r"^([A-Za-z_]\w*(?:Error|Exception|Interrupt|Exit))\b")


def error_kind(stderr: str) -> str | None:
    """錯誤訊息最下面那一行的錯誤種類（TypeError、SyntaxError…），找不到是 None。"""
    for line in reversed(_text(stderr).splitlines()):
        m = ERROR_LINE.match(line.strip())
        if m:
            return m.group(1)
    return None


class RunCheck(Check):
    def own_timeout(self) -> float | None:
        """1-10 起：checks.json 這一題寫了 timeout（秒）就用它（再上限環境的逾時），沒寫照舊用環境的（預設 30 秒）。"""
        t = self.spec.get("timeout")
        return min(self.ctx.env.timeout, float(t)) if t else None

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
        swap = self.spec.get("swap")
        if swap:
            # 1-C1 第三部分：把學員程式裡的一行（例如 total = 1730）換成別的金額，再跑一次，看是不是用算的、不是把答案寫死。
            # 換過的程式寫在系統的暫存資料夾（同一個檔名），不寫帳本、也不寫課程資料夾；只對寫了 swap 的 checks.json 生效
            src = read_student_text(path)
            pat = re.compile(swap["find"], re.MULTILINE)
            if not pat.search(src):
                r.detail = swap.get("missing", "找不到題目規定要有的那一行。")
                return
            tmpdir = Path(tempfile.mkdtemp(prefix="plusform-swap-"))
            try:
                moved = tmpdir / path.name
                moved.write_text(pat.sub(swap["to"], src, count=1), encoding="utf-8")
                p = self.ctx.env.run_file(moved, stdin=stdin)
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)
            feed = swap.get("feed", "") + ("\n  " if swap.get("feed") else "") + feed
        else:
            p = self.ctx.env.run_file(path, stdin=stdin, timeout=self.own_timeout())
        stuck_hint = f"\n  提示：{self.spec['stuck_hint']}" if self.spec.get("stuck_hint") else ""   # 1-10：卡住時的白話（只對寫了它的題目）
        if p.timed_out:
            secs = self.own_timeout() or self.ctx.env.timeout
            self.ctx.stuck[str(path)] = f"跑了 {secs:.0f} 秒還沒結束"
            r.detail = feed + f"跑了 {secs:.0f} 秒還沒結束，被停下來了：可能有無窮迴圈。" + stuck_hint
            return
        if p.overflow:
            self.ctx.stuck[str(path)] = "印了太多東西被停下來"
            r.detail = feed + "你的程式印了太多東西，被停下來了：可能是迴圈沒停下來。" + stuck_hint
            return
        if p.returncode != 0:
            r.data["error"] = error_kind(p.stderr)   # 1-C1 的矯正包照錯誤種類（SyntaxError、NameError、TypeError…）指回原課
            if "EOFError" in p.stderr and self.spec.get("eof_hint"):   # 1-10：迴圈一直問、輸入讀完了還沒停（只對寫了它的題目）
                n_in = len(stdin.splitlines())
                r.detail = feed + f"給它的 {n_in} 行輸入都讀完了，你的程式還在問（EOFError）：迴圈沒有停下來。\n  提示：{self.spec['eof_hint']}"
                return
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
        elif self.spec.get("time_it") == "timer":   # 1-7 的計時題：記下作答檔最後一次存檔的時間（check.py 照 timer 開始的時間算分鐘）
            r.data["mtime"] = path.stat().st_mtime


# ---------------- parsons（拼圖，2026-11-15，1-11 起；只對寫了 type parsons 的 checks.json 生效） ----------------

def _flat_code(text: str) -> str:
    """比對拼圖的一行：NFKC 後拿掉所有空白（學員多打或少打一個空格不算改字；縮排另外檢查）。"""
    return "".join(unicodedata.normalize("NFKC", text).split())


class ParsonsCheck(Check):
    """學員把打亂的程式行排回正確的順序、自己加縮排（每一層四個空格）。兩題：
      order：題目給的行一行不少、一行不多、沒有改字，縮排是四個空格的倍數，而且 Python 讀得懂（沒有 IndentationError／SyntaxError）
      run：  排好跑起來，印出來的跟 expect_exact 一模一樣（排法不只一種也沒關係，照跑出來的結果判）
    spec：file、lines（題目給的行，不含縮排）、expect_exact、timeout（秒，選填）、hint（選填）。# 開頭的說明行和空行不算。"""

    def plan(self):
        s = self.spec
        return [self.stub("order", s.get("desc_order", "拼圖：每一行都用上、沒有改字，排好以後 Python 讀得懂")),
                self.stub("run", s.get("desc_run", "拼圖：排好跑出來跟範例一模一樣"))]

    def run(self, results):
        order_r, run_r = results
        rel = self.spec["file"]
        path = self.ctx.student(rel)
        if not path.is_file():
            order_r.detail = run_r.detail = self.ctx.missing(rel, self.spec.get("missing_hint"))
            return
        source = read_student_text(path)
        body = [(i, raw.rstrip("\r\n")) for i, raw in enumerate(source.splitlines(), start=1)
                if raw.strip() and not raw.strip().startswith("#")]
        given = [_flat_code(x) for x in self.spec["lines"]]
        shown = {_flat_code(x): x for x in self.spec["lines"]}
        left = list(given)
        problems = []
        for i, raw in body:
            k = _flat_code(raw)
            if k in left:
                left.remove(k)
            else:
                problems.append(f"第 {i} 行「{raw.strip()}」不是拼圖裡的行（或是同一行用了兩次）。"
                                "拼圖只能搬動和縮排，不能改字、不能多寫。")
        for k in left:
            problems.append(f"少了「{shown[k]}」這一行：題目給的每一行都要用上。")
        for i, raw in body:
            lead = raw[: len(raw) - len(raw.lstrip())]
            if "\t" in lead:
                problems.append(f"第 {i} 行用了 Tab 縮排：每一層請打四個空格（VS Code 按 Tab 也會變成四個空格）。")
            elif len(lead) % 4:
                problems.append(f"第 {i} 行往右縮了 {len(lead)} 格：每一層縮四格（4、8、12……）。")
        if not problems:
            try:
                ast.parse(source)
            except SyntaxError as exc:
                bad = exc.text.strip() if exc.text else ""
                if isinstance(exc, IndentationError) or "indent" in (exc.msg or ""):
                    problems.append(f"Python 讀到第 {exc.lineno} 行就說縮排不對（{type(exc).__name__}）：{bad}\n"
                                    "  for 那一行最後有冒號，下一行要往右縮四格；同一層的行要對齊。")
                else:
                    problems.append(f"第 {exc.lineno} 行有語法錯誤（{exc.msg}）：{bad}")
        order_r.ok = not problems
        if problems:
            order_r.detail = first_problem(problems)
            run_r.detail = "先把上一題（每一行都用上、縮排對）修好，再看跑出來的結果。"
            return
        t = self.spec.get("timeout")
        p = self.ctx.env.run_file(path, timeout=min(self.ctx.env.timeout, float(t)) if t else None)
        hint = f"\n  提示：{self.spec['hint']}" if self.spec.get("hint") else ""
        if p.timed_out or p.overflow:
            run_r.detail = "跑了太久或印了太多東西，被停下來了：看看是不是排成了停不下來的樣子。" + hint
            return
        if p.returncode != 0:
            run_r.detail = crash_story(p, "") + hint
            return
        want = output_lines("\n".join(self.spec["expect_exact"]))
        got = output_lines(p.stdout)
        run_r.ok = got == want
        if not run_r.ok:
            mine = "\n".join("    " + ln.rstrip() for ln in p.stdout.splitlines() if ln.strip()) or "    （什麼都沒印）"
            run_r.detail = ("排好跑出來跟範例不一樣。\n  範例：\n" + "\n".join("    " + w for w in want)
                            + f"\n  你的（{len(got)} 行）：\n" + mine + hint)


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
CHAFF_NOUN = {"expected_text": "預期輸出", "inputs_text": "預期輸出", "cases": "案例"}   # 總結那一行的名詞（assert／其他模式是「檢查」）
TEXT_MODES = ("expected_text", "inputs_text")   # 一行一行比整段輸出的模式（inputs_text 是 1-6 加的：先把 inputs.txt 餵給程式）

CURLY_QUOTES = "“”‘’「」『』〝〞＂＇"
ARROWS = ("->", "→", "=>")
TYPE_LABEL = {"int": "整數", "float": "小數", "str": "文字", "bool": "布林", "NoneType": "沒有值"}


def split_case_line(raw: str) -> tuple[str, str, str | None]:
    """cases 的一行拆成（程式那一段, 行尾註解, 用到的中文引號）。引號裡的 # 不算註解；引號外面的字做 NFKC（全形箭頭、全形空白）。"""
    code, quote, i = [], None, 0
    text = raw.rstrip("\r\n")
    while i < len(text):
        ch = text[i]
        if quote:
            code.append(ch)
            if ch == "\\" and i + 1 < len(text):
                code.append(text[i + 1])
                i += 1
            elif ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            code.append(ch)
        elif ch == "#":
            return "".join(code), text[i:], None
        elif ch in CURLY_QUOTES:
            return "".join(code), "", ch
        else:
            code.append(unicodedata.normalize("NFKC", ch))
        i += 1
    return "".join(code), "", None


def split_arrow(code: str) -> tuple[str, str | None]:
    """在引號外面找第一個箭頭（-> → =>），拆成左右兩邊；找不到就回（整段, None）。"""
    quote, i = None, 0
    while i < len(code):
        ch = code[i]
        if quote:
            if ch == "\\":
                i += 1
            elif ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        else:
            for a in ARROWS:
                if code.startswith(a, i):
                    return code[:i], code[i + len(a):]
        i += 1
    return code, None


def typed(value, type_name: str | None = None, bare: bool = False) -> str:
    """給新手看的值：文字加雙引號；後面標型別（整數 int／小數 float／文字 str）。bare＝只要值、不標型別。"""
    name = type_name or ("NoneType" if value is None else type(value).__name__)
    shown = '"' + value + '"' if isinstance(value, str) and name == "str" else repr(value) if name in ("float",) else str(value)
    if bare:
        return shown
    label = TYPE_LABEL.get(name)
    return f"{shown}（{label} {name}）" if label and name != "NoneType" else f"{shown}（{label or name}）"


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
        self._stuck_names: list[str] = []   # 1-10 stuck_note：跑到逾時被停下來的版本
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
                        if self.spec.get("no_marks"):   # 1-8：還沒教特殊作答，行尾的註解一律當成一般的檢查
                            kind = None
                        if kind:
                            marks.append(Mark(stmt.lineno, kind, text, stmt))
                        else:
                            checks.append(StudentCheck(stmt.lineno, text, stmt=stmt))
            elif self.mode == "expected_text":
                checks, unfinished = self.parse_expected_text(lines)
            elif self.mode == "inputs_text":
                checks, unfinished = self.parse_expected_text(lines)
                problem = self.read_inputs()
            elif self.mode == "cases":
                checks, marks, unfinished, problem = self.parse_cases(lines)
            elif self.mode == "table_facts":
                checks, unfinished, problem = self.parse_facts(lines)
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

    # ----- expected_text（2026-11-14，1-1 第③圈）：整段預期輸出一行一行比，連空行一起 -----
    @staticmethod
    def norm_out(text: str) -> str:
        """一行輸出的比法：NFKC（全形冒號＝半形）、去掉行尾空白；行內的空格要一模一樣（不像 norm_line 會併掉空白）。"""
        return unicodedata.normalize("NFKC", text).rstrip()

    @classmethod
    def out_rows(cls, text: str) -> list[str]:
        """程式印出來的字 → 一行一行（換行統一成 \n；頭尾的空行拿掉，中間的空行留著）。"""
        rows = [cls.norm_out(x) for x in _text(text).replace("\r\n", "\n").replace("\r", "\n").split("\n")]
        while rows and not rows[-1]:
            rows.pop()
        while rows and not rows[0]:
            rows.pop(0)
        return rows

    def parse_expected_text(self, lines: list[str]) -> tuple[list[StudentCheck], int]:
        """學員寫的預期輸出：# 開頭是說明行（不比）、有「？」的行算還沒寫完；頭尾空行拿掉、中間空行留著。
        第 k 行就是一條檢查（text 存原本的字，比的時候才 norm_out）；最後多一條「總行數一樣」（line＝0、must＝False 當記號）。"""
        body: list[tuple[int, str]] = []
        unfinished = 0
        for i, raw in enumerate(lines, start=1):
            if raw.strip().startswith("#"):
                continue
            if "？" in raw or "?" in raw:
                unfinished += 1
                continue
            body.append((i, raw.rstrip("\r\n")))
        while body and not body[-1][1].strip():
            body.pop()
        while body and not body[0][1].strip():
            body.pop(0)
        checks = [StudentCheck(i, text) for i, text in body]
        if checks:
            checks.append(StudentCheck(0, f"（一共 {len(checks)} 行）", must=False))
        return checks, unfinished

    def expected_rows(self, checks: list[StudentCheck], printed: list[str], crashed: bool, norm=None) -> list[dict]:
        """每一條檢查在這個版本上成不成立。當掉的版本照「當掉前印出來的」比，缺的行算不一樣（不整版算 error）。
        norm：學員那一行怎麼正規化（預設 norm_out；1-6 的 inputs_text 另外拿掉開頭的提示字）。"""
        norm = norm or self.norm_out
        body = [c for c in checks if c.line]
        rows = []
        for k, c in enumerate(checks):
            if not c.line:   # 總行數
                ok = len(printed) == len(body)
                rows.append({"status": "pass" if ok else "fail", "why": "count", "got_n": len(printed), "crashed": crashed})
                continue
            got = printed[k] if k < len(printed) else None
            ok = got is not None and got == norm(c.text)
            rows.append({"status": "pass" if ok else "fail", "why": "missing" if got is None else "line", "row": k + 1, "crashed": crashed})
        return rows

    # ----- inputs_text（2026-11-15，1-6 第③圈）：學員寫 inputs.txt（要打的字）和 expected.txt（預期輸出），
    #       check 自己用 subprocess 把 inputs.txt 餵給正確版和 3 個壞版本（不靠 shell 的 <，Windows 的 PowerShell 也能跑），印出來的一行一行比 -----
    def read_inputs(self) -> str | None:
        """讀 inputs.txt：一行就是程式問一次時要打的字，原樣餵進去（跟 uv run 程式 < inputs.txt 一樣）；換行統一成 \n。
        回傳 None 或一句白話的問題。# 開頭的行、「？」都不收：inputs.txt 的每一行都會被當成打進去的字。"""
        rel = self.spec["inputs_file"]
        name = Path(rel).name
        try:
            path = self.ctx.student(rel)
        except NotReady as exc:
            return str(exc)
        if not path.is_file():
            return self.ctx.missing(rel)
        try:
            text = read_student_text(path)
        except NotReady as exc:
            return str(exc)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        rows = text.split("\n")
        if rows and rows[-1] == "":
            rows = rows[:-1]
        if not any(r.strip() for r in rows):
            return f"{name} 是空的。一行寫一個要打的字，照程式問的順序（{or_list(self.spec.get('prompts', []))}）。"
        for i, r in enumerate(rows, start=1):
            if r.strip().startswith("#"):
                return (f"{name} 第 {i} 行是 # 開頭的說明。{name} 的每一行都會被當成你打的字餵給程式，"
                        "不能寫說明；說明寫在 expected.txt 的 # 那幾行。")
            if "？" in r or "?" in r:
                return f"{name} 第 {i} 行還是「？」：換成你要打的字。"
        self._stdin = "\n".join(rows) + "\n"
        self._n_inputs = len(rows)
        return None

    def strip_prompts(self, row: str) -> str:
        """拿掉一行開頭的提示字（從檔案讀的時候，input() 的提示字後面不換行，會一個接一個黏在下一行印的字前面）。"""
        prompts = [unicodedata.normalize("NFKC", x) for x in self.spec.get("prompts", []) if x]
        again = True
        while again:
            again = False
            for pr in prompts:
                if row.startswith(pr):
                    row, again = row[len(pr):], True
        return row

    def cmp_line(self, text: str) -> str:
        return self.strip_prompts(self.norm_out(text))

    def prompt_rows(self, stdout: str) -> list[str]:
        rows = [self.strip_prompts(x) for x in self.out_rows(stdout)]
        while rows and not rows[-1]:
            rows.pop()
        while rows and not rows[0]:
            rows.pop(0)
        return rows

    def ref_crash_text(self, p: Proc) -> str:
        """正確版吃了學員的 inputs.txt 就當掉：多半是 inputs.txt 的行數不夠，或寫了需求卡說不會有的字。"""
        name = Path(self.spec["inputs_file"]).name
        asks = self.spec.get("prompts", [])
        if p.timed_out:
            return f"正確版跑了 {self.version_timeout():.0f} 秒還沒結束。先確定 0-5 的環境檢查都過了（uv run check.py env）。"
        if "EOFError" in p.stderr and self.spec.get("eof_hint"):   # 1-10：迴圈會一直問，問幾次不固定
            return (f"{name} 的 {self._n_inputs} 行都讀完了，正確版還在問，讀到檔案最後就當掉了（EOFError）。"
                    f"\n  {self.spec['eof_hint']}")
        if "EOFError" in p.stderr:
            return (f"{name} 只有 {self._n_inputs} 行，程式要問 {len(asks)} 次（{or_list(asks)}），字不夠，正確版讀到檔案最後就當掉了（EOFError）。"
                    f"\n  一行寫一個要打的字，照它問的順序。")
        last = next((ln.strip() for ln in reversed(p.stderr.splitlines()) if ln.strip()), "")
        return (f"你的 {name} 讓正確版也當掉了（最後一行：{last}）。\n"
                f"  {self.spec.get('crash_hint', '看看是不是寫了需求卡說不會出現的字。')}")

    # ----- table_facts（2026-11-15，1-11 第③圈）：學員先不跑程式，照需求卡寫下表格的幾件事（應該有幾列、某一格是多少），
    #       check 跑正確版和 3 個壞版本（不餵輸入），數印出來的列、找那一格，一件一件比。只對寫了 mode table_facts 的 checks.json 生效 -----
    @staticmethod
    def fact_key(text: str) -> str:
        return "".join(unicodedata.normalize("NFKC", text).split())

    def parse_facts(self, lines: list[str]) -> tuple[list[StudentCheck], int, str | None]:
        """每一行「冒號前面的字：數字」。冒號前面要照原本的寫（spec 的 facts[].label），只改「？」；# 開頭是說明行。
        回傳（檢查, 還沒寫完的行數, 一句白話的問題或 None）。self._facts[行號] = (fact, 學員寫的數字)。"""
        facts = {self.fact_key(f["label"]): f for f in self.spec["facts"]}
        labels = "「" + "」「".join(f["label"] for f in self.spec["facts"]) + "」"
        checks: list[StudentCheck] = []
        unfinished = 0
        seen: set[str] = set()
        self._facts: dict[int, tuple[dict, int]] = {}
        for i, raw in enumerate(lines, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            flat = unicodedata.normalize("NFKC", line)
            if ":" not in flat:
                return checks, unfinished, f"第 {i} 行「{line}」少了冒號。照原本的格式「開頭：數字」寫，只改「？」那裡。"
            left, right = flat.split(":", 1)
            key = self.fact_key(left)
            if key not in facts:
                return checks, unfinished, f"第 {i} 行「{line}」：冒號前面的字被改到了，只要改「？」就好。\n  冒號前面照原本的寫：{labels}。"
            if key in seen:
                return checks, unfinished, f"第 {i} 行「{line}」：{facts[key]['label']}寫了兩次，留一行就好。"
            seen.add(key)
            if "?" in right:
                unfinished += 1
                continue
            val = "".join(right.split()).replace(",", "")
            m = re.fullmatch(r"(-?\d+)(列|元|格|行)?", val)
            if not m:
                return checks, unfinished, (f"第 {i} 行「{line}」：冒號後面寫一個整數就好（例如 5），"
                                            "不要寫算式或文字。")
            checks.append(StudentCheck(i, line))
            self._facts[i] = (facts[key], int(m.group(1)))
        return checks, unfinished, None

    @staticmethod
    def table_rows(stdout: str) -> list[str]:
        """印出來的字 → 一列一列（空白的列不算，跟需求卡「每天一列」的數法一樣）。"""
        return [unicodedata.normalize("NFKC", x).strip() for x in _text(stdout).replace("\r\n", "\n").split("\n") if x.strip()]

    @staticmethod
    def fact_value(fact: dict, rows: list[str]) -> int | None:
        """這個版本印出來的表，這一件事是多少（找不到是 None）：
        rows＝有幾列；cell＝從 fact["row"]（例如「第 3 天」）那個標籤後面開始、到下一個同樣的標籤（第 N 天）之前，冒號後面第 col 個數字。
        照標籤找、不照換行找：同一天的格子被換行拆成好幾列（print() 縮錯層），那一格的數字一樣找得到，只有列數不一樣。"""
        if fact["kind"] == "rows":
            return len(rows)
        words = unicodedata.normalize("NFKC", fact["row"]).split()
        head = r"\s*".join(re.escape(x) for x in words) + r"(?!\d)"
        label = r"\s*".join(r"\d+" if x.isdigit() else re.escape(x) for x in words) + r"(?!\d)"   # 第 3 天 → 第 N 天
        text = "\n".join(rows)
        m = re.search(head, text)
        if not m:
            return None
        rest = text[m.end():]
        nxt = re.search(label, rest)
        if nxt:
            rest = rest[:nxt.start()]
        rest = rest.split(":", 1)[1] if ":" in rest.split("\n", 1)[0] else rest
        nums = re.findall(r"-?\d+", rest)
        k = int(fact["col"]) - 1
        return int(nums[k]) if 0 <= k < len(nums) else None

    # ----- cases（2026-11-14，1-3 第③圈）：案例表「輸入 -> 應該變成」，check.py 把輸入丟給各版本的固定函式，連型別一起比 -----
    def parse_cases(self, lines: list[str]) -> tuple[list[StudentCheck], list[Mark], int, str | None]:
        """每一行：左邊是丟進函式的值（1-3 是金額文字，要加引號），右邊是應該變成的值，中間用 -> 隔開。
        # 開頭是說明行；有「？」的行算還沒寫完；行尾的 # 已知會當掉／# 需求有問題 是特殊作答（右邊可以不寫）。
        左右兩邊都用 ast.literal_eval 讀（整數、小數、文字、True／False、None），看不懂就回一句白話（第一個看不懂的那一行）。"""
        checks: list[StudentCheck] = []
        marks: list[Mark] = []
        unfinished = 0
        self._cases: dict[int, tuple] = {}
        want = self.spec.get("input_type", "str")
        for i, raw in enumerate(lines, start=1):
            if not raw.strip() or raw.strip().startswith("#"):
                continue
            code, comment, bad_quote = split_case_line(raw)
            kind = _mark_in(comment) if comment else None
            if bad_quote:
                return checks, marks, unfinished, (f"第 {i} 行用了中文的引號（{bad_quote}）。"
                                                  "Python 的文字要用鍵盤上的半形引號 \" 或 '，例如 \"120\"。")
            if not kind and ("？" in code or "?" in code):
                unfinished += 1
                continue
            left, right = split_arrow(code)
            if right is None and not kind:
                return checks, marks, unfinished, (f"第 {i} 行少了箭頭。每一行寫成：左邊的輸入 -> 右邊應該變成的值，"
                                                  "例如 \"120\" -> 120（箭頭是減號加大於 ->）。")
            try:
                inp = ast.literal_eval(left.strip())
            except (ValueError, SyntaxError, MemoryError, RecursionError):
                return checks, marks, unfinished, (f"第 {i} 行左邊「{left.strip()}」看不懂。"
                                                  + self.spec.get("input_hint", "左邊是要丟進轉換機的金額文字，前後要加引號，例如 \"120\"。"))   # 1-5 寫自己的說法
            if want == "str" and not isinstance(inp, str):
                return checks, marks, unfinished, (f"第 {i} 行左邊的 {left.strip()} 沒有引號，是數字。"
                                                  f"轉換機收的是文字：寫成 \"{left.strip()}\"。")
            if want == "int" and (isinstance(inp, bool) or not isinstance(inp, int)):   # 1-4：左邊是整數金額
                why = ("有引號，是文字。分帳機收的是整數：把引號拿掉" if isinstance(inp, str) else
                       "有小數點。帳本只記整數元：寫整數" if isinstance(inp, float) else "不是整數。左邊寫一個整數金額")
                return checks, marks, unfinished, f"第 {i} 行左邊的 {left.strip()} {why}，例如 1000。"
            if kind:
                marks.append(Mark(i, kind, raw.strip(), None))
                self._cases[i] = (inp, None)
                continue
            n_ints = int(self.spec.get("expect_ints", 0))   # 1-4：右邊是 n 個整數、用逗號隔開（三個人各付多少）
            if n_ints:
                right = right.replace("、", ",")
            tup = self.spec.get("expect_tuple")   # 1-5：右邊是幾個值用逗號隔開，每個值的型別照順序（品項文字、金額整數）
            if tup:
                exp, why = self.parse_tuple(right, tup)
                if why:
                    return checks, marks, unfinished, f"第 {i} 行{why}"
                checks.append(StudentCheck(i, raw.strip()))
                self._cases[i] = (inp, exp)
                continue
            try:
                exp = ast.literal_eval(right.strip())
            except (ValueError, SyntaxError, MemoryError, RecursionError):
                if n_ints:
                    return checks, marks, unfinished, (f"第 {i} 行右邊「{right.strip()}」看不懂。"
                                                      f"右邊寫 {n_ints} 個整數，中間用逗號隔開，例如 334, 333, 333（不要寫「元」）。")
                return checks, marks, unfinished, (f"第 {i} 行右邊「{right.strip()}」看不懂。"
                                                  "整數直接寫數字（120）；文字才加引號（\"120\"）；不要寫單位「元」。")
            if n_ints:
                exp = tuple(exp) if isinstance(exp, (list, tuple)) else (exp,)
                if len(exp) != n_ints:
                    return checks, marks, unfinished, (f"第 {i} 行右邊寫了 {len(exp)} 個數字。"
                                                      f"要寫 {n_ints} 個人各付多少，用逗號隔開，例如 334, 333, 333。")
                if any(isinstance(x, bool) or not isinstance(x, int) for x in exp):
                    return checks, marks, unfinished, (f"第 {i} 行右邊「{right.strip()}」：每個人付的都要是整數元，"
                                                      "不加引號、不加小數點，例如 334, 333, 333。")
            checks.append(StudentCheck(i, raw.strip()))
            self._cases[i] = (inp, exp)
        return checks, marks, unfinished, None

    @staticmethod
    def parse_tuple(right: str, tup: dict) -> tuple[tuple | None, str | None]:
        """1-5 的 expect_tuple：右邊「"午餐", 120」→ ("午餐", 120)。tup＝{types: ["str", "int"], names: ["品項", "金額"], example: "\"午餐\", 120"}。
        回傳（值, None）或（None, 白話的錯誤說明，接在「第 N 行」後面）。"""
        types, names, ex = tup["types"], tup["names"], tup.get("example", "")
        both = "和".join(names)
        rule = "；".join(f"{n}是{'文字，要加引號' if t == 'str' else '整數，不加引號、不寫「元」'}" for n, t in zip(names, types))
        try:
            exp = ast.literal_eval(right.replace("、", ",").strip())
        except (ValueError, SyntaxError, MemoryError, RecursionError):
            return None, f"右邊「{right.strip()}」看不懂。右邊寫{both}，中間用逗號隔開（{rule}），例如 {ex}。"
        exp = tuple(exp) if isinstance(exp, (list, tuple)) else (exp,)
        if len(exp) != len(types):
            return None, f"右邊寫了 {len(exp)} 個值。要寫{both}，一共 {len(types)} 個，用逗號隔開，例如 {ex}。"
        for v, t, n in zip(exp, types, names):
            if t == "str" and not isinstance(v, str):
                return None, f"右邊的{n} {v!r} 不是文字。{n}要加引號，例如 {ex}。"
            if t == "int" and (isinstance(v, bool) or not isinstance(v, int)):
                kind = "有引號，是文字" if isinstance(v, str) else "有小數點" if isinstance(v, float) else "不是整數"
                return None, f"右邊的{n} {typed(v, bare=True)} {kind}。{n}是整數：不加引號、不寫「元」，例如 {ex}。"
        return exp, None

    def case_rows(self, path: Path, lines: list[int]) -> dict[int, dict]:
        """用一個程序跑一個版本：每一行的輸入丟進固定的函式，回傳 {行號: 結果}（連型別一起比）。"""
        cases = [{"args": [self._cases[ln][0]], "expect": self._cases[ln][1]} for ln in lines]
        timeout = self.version_timeout()
        req = {"op": "call", "file": str(path), "module": self.spec["module"], "func": self.spec["func"], "cases": cases, "strict_type": True}
        if self.spec.get("expect_ints") or self.spec.get("expect_tuple"):
            req["seq_as_list"] = True   # 1-4：函式交回 (334, 333, 333)，JSON 只有 list，兩邊都當 list 比、每個數字的型別也比（1-5 的 ("午餐", 120) 同樣）
        reply = self.ctx.env.runner_raw(req, timeout=timeout)
        data = reply.result
        if data is None or "runner_error" in (data or {}):
            why = (f"跑了 {timeout:.0f} 秒還沒結束" if reply.proc.timed_out else
                   "印了太多東西被停下來" if reply.proc.overflow else
                   "檢查程式出錯了：" + ((data or {}).get("runner_error") or tail(reply.proc.stderr, 2).strip()))
            return {ln: {"status": "error", "error": why, "stuck": True} for ln in lines}
        if data.get("load_error"):
            err = data["load_error"]
            return {ln: {"status": "error", "error": f"這個版本載入就出錯了（{err.get('msg')}）"} for ln in lines}
        out = {}
        for ln, case in zip(lines, data["cases"]):
            if "error" in case:
                out[ln] = {"status": "error", "error": case["error"]}
            else:
                out[ln] = {"status": "pass" if case.get("ok") else "fail", "got": case.get("got"), "got_type": case.get("type")}
        return out

    def plan(self):
        parsed = self.parse()
        if self.mode == "cases":
            out = [
                self.stub("count", f"至少寫 {self.min} 組案例"),
                self.stub("wheat", "你寫的案例，正確版都算得對"),
            ]
            for i, _m in enumerate(self.mutants, start=1):
                out.append(self.stub(f"m{i}", f"抓到第 {i} 個壞版本"))
            for mk in parsed.marks:
                stub = self.stub(f"s{mk.line}", f"第 {mk.line} 行標了「{mk.kind}」")
                stub.special = True
                out.append(stub)
            need = int(self.spec.get("min_marks", 0))
            if need and len([m for m in parsed.marks if m.kind == "已知會當掉"]) < need:
                out.append(self.stub("smin", f"至少 {need} 組標「已知會當掉」"))
            return out
        if self.mode in TEXT_MODES:
            out = [
                self.stub("count", f"預期輸出至少寫 {self.min} 行"),
                self.stub("wheat", "你寫的預期輸出，跟正確版印出來的一模一樣" if self.mode == "expected_text"
                          else "inputs.txt 餵給正確版，印出來的跟你的預期輸出一模一樣"),
            ]
            for i, _m in enumerate(self.mutants, start=1):
                out.append(self.stub(f"m{i}", f"抓到第 {i} 個壞版本"))
            return out
        if self.mode == "table_facts":   # 1-11：寫的是表格的幾件事（應該有幾列、某一格是多少）
            out = [
                self.stub("count", f"至少寫 {self.min} 件事（只改「？」）"),
                self.stub("wheat", "你寫的每一件事，正確版都對得上"),
            ]
            for i, _m in enumerate(self.mutants, start=1):
                out.append(self.stub(f"m{i}", f"抓到第 {i} 個壞版本"))
            return out
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
        req = {
            "op": "asserts",
            "checks_file": str(self.ctx.student(self.spec["student_file"])),
            "module": self.spec["module"],
            "impl": str(impl),
        }
        if self.spec.get("bool_hints"):   # 1-8：只寫 assert over_budget(...)／assert not over_budget(...) 也報出交回的值
            req["got_bare"] = True
        reply = self.ctx.env.runner_raw(req, timeout=timeout)
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
        elif self.mode == "expected_text":
            for name, path in impls.items():
                p = self.ctx.env.run_file(path, timeout=self.version_timeout())
                crashed = p.returncode != 0 or p.stopped
                if name == "reference" and crashed:
                    out[name] = [{"status": "error", "error": "正確版跑不起來"} for _c in checks]
                    continue
                out[name] = self.expected_rows(checks, self.out_rows(p.stdout), crashed)
        elif self.mode == "inputs_text":
            for name, path in impls.items():
                p = self.ctx.env.run_file(path, stdin=self._stdin, timeout=self.version_timeout())   # subprocess 餵 stdin，不靠 shell 的 <
                crashed = p.returncode != 0 or p.stopped
                if name == "reference" and crashed:
                    self._ref_err = self.ref_crash_text(p)
                    out[name] = [{"status": "error", "error": self._ref_err} for _c in checks]
                    continue
                rows = self.expected_rows(checks, self.prompt_rows(p.stdout), crashed, norm=self.cmp_line)
                if self.spec.get("stuck_note") and p.timed_out:   # 1-10：卡在無窮迴圈、被逾時停下來，不是當掉
                    rows = [dict(x, crashed=False, stuck=True) for x in rows]
                    self._stuck_names.append(name)
                out[name] = rows
        elif self.mode == "cases":
            lines = sorted([c.line for c in checks] + [m.line for m in marks])
            for name, path in impls.items():
                by_line = self.case_rows(path, lines)
                out[name] = [by_line[c.line] for c in checks]
                if name == "reference":
                    mark_status = {m.line: by_line[m.line] for m in marks}
        elif self.mode == "table_facts":
            for name, path in impls.items():
                p = self.ctx.env.run_file(path, timeout=self.version_timeout())
                crashed = p.returncode != 0 or p.stopped
                if name == "reference" and crashed:
                    out[name] = [{"status": "error", "error": "正確版跑不起來"} for _c in checks]
                    continue
                rows_out = self.table_rows(p.stdout)
                rows = []
                for c in checks:
                    fact, want = self._facts[c.line]
                    got = self.fact_value(fact, rows_out)
                    rows.append({"status": "pass" if got == want else "fail", "got": got, "crashed": crashed})
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
            marks_ok = not self.spec.get("no_marks")   # 1-8：還沒教特殊作答，不提「# 已知會當掉」「# 需求有問題」
            if st.get("not_run"):
                return msg + "前面卡住了，這一行沒有跑到。"
            if st.get("stuck"):
                return msg + f"在正確版上{err}。如果你的檢查裡有迴圈，看看它停不停得下來。"
            if st.get("status") == "error":
                if "NameError" in err and not self.has_import:
                    return msg + (f"程式不認得這個名字（{err}）。"
                                  f"最上面那行 from {self.spec.get('module')} import … 要留著，不要刪掉。")
                if self.spec.get("bool_hints"):
                    m = re.search(r"NameError: name '(\w+)' is not defined", err)
                    if m and m.group(1).lower() in ("true", "false", "ture", "flase"):
                        return msg + (f"程式不認得 {m.group(1)} 這個名字。True、False 第一個字母要大寫，"
                                      "不加引號（1-3 學過）。")
                if not marks_ok:
                    return msg + f"在正確版上就會當掉（{err}）。看看這一行是不是打錯字，或括號裡少放了東西。"
                return (msg + f"在正確版上就不成立，而且會當掉（{err}）。\n"
                        "  如果你本來就是要測「正確版也會當掉」的情況，在這行最後加上「# 已知會當掉」。")
            msg += "在正確版上就不成立"
            if st.get("got") is not None:
                if self.spec.get("bool_hints") and c.stmt is not None and not isinstance(c.stmt.test, ast.Compare):
                    call = c.stmt.test.operand if isinstance(c.stmt.test, ast.UnaryOp) else c.stmt.test
                    msg += f"（{ast.unparse(call)} 在正確版交回 {show(st['got'])}）"
                else:
                    msg += f"（正確版算出來是{show(st['got'])}）"
            if self.spec.get("bool_hints") and c.stmt is not None and isinstance(c.stmt.test, ast.Compare):
                right = c.stmt.test.comparators[0]
                if isinstance(right, ast.Constant) and isinstance(right.value, str) and right.value.strip().lower() in ("true", "false"):
                    return msg + (f"。\n  True、False 不加引號：加了引號的 \"{right.value}\" 是文字（1-3 學過），"
                                  "跟 True、False 永遠不一樣。")
            if not marks_ok:
                return msg + "。\n  正確版不會錯，所以是這條檢查要改：再對一次需求卡（剛好等於的時候算哪一邊？）。"
            return msg + "。\n  正確版不會錯，所以是這條檢查要改；如果你覺得是需求沒講清楚，在行尾加上「# 需求有問題」。"
        if self.mode == "cases":
            inp, exp = self._cases[c.line]
            call = f"{self.spec['func']}({typed(inp, bare=True)})"
            if self.spec.get("expect_ints") and st.get("status") not in ("error",) and not st.get("stuck"):   # 1-4：三個人各付多少
                got = st.get("got")
                shown = ", ".join(str(x) for x in got) if isinstance(got, (list, tuple)) else typed(got, st.get("got_type"))
                return (f"第 {c.line} 行：{call} 正確版算出來是 {shown}，你寫的是 {', '.join(str(x) for x in exp)}。\n"
                        "  再對一次需求：先用 // 算每人付多少、用 % 算零頭，零頭從第一個人開始，一人多 1 元。")
            tup = self.spec.get("expect_tuple")
            if tup and st.get("status") not in ("error",) and not st.get("stuck"):   # 1-5：拆出品項和金額
                got = st.get("got")
                shown = ", ".join(typed(x, bare=True) for x in got) if isinstance(got, (list, tuple)) else typed(got, st.get("got_type"))
                rule = "，".join(f"{n}是{'文字（加引號）' if t == 'str' else '整數（不加引號）'}" for n, t in zip(tup["names"], tup["types"]))
                return (f"第 {c.line} 行：{call} 正確版拆出來是 {shown}，你寫的是 {', '.join(typed(x, bare=True) for x in exp)}。\n"
                        f"  再對一次：{rule}，前後多的空白不算。")
            if st.get("stuck"):
                return f"第 {c.line} 行：{call} 在正確版上{st.get('error')}。先確定 0-5 的環境檢查都過了（uv run check.py env）。"
            if st.get("status") == "error":
                return (f"第 {c.line} 行：{call} 連正確版都會當掉（{st.get('error')}）。\n"
                        f"  如果你本來就是要找「正確版也會當掉」的{self.spec.get('input_noun', '金額')}，在這行最後加上「# 已知會當掉」。")
            got = st.get("got")
            msg = f"第 {c.line} 行：{call} 正確版變成 {typed(got, st.get('got_type'))}，你寫的是 {typed(exp)}。"
            if got == exp or str(got) == str(exp):   # 120 對 120.0、120 對 "120"：數字一樣、型別不一樣
                msg += "\n  數字一樣、型別不一樣：沒有引號的 120 是整數，\"120\" 是文字，120.0 是小數。"
            return msg
        if self.mode == "table_facts":   # 1-11：不講正確的數字，只給提示（spec 的 facts[].hint）
            if st.get("status") == "error":
                return "正確版在你的帳本裡跑不起來，先確定 0-5 的環境檢查都過了（uv run check.py env）。"
            fact, want = self._facts[c.line]
            return (f"第 {c.line} 行「{c.text}」：跟正確版印出來的不一樣。\n"
                    f"  提示：{fact.get('hint', '再對一次需求卡。')}")
        if self.mode == "inputs_text" and st.get("status") == "error":
            return st.get("error") or "正確版跑不起來。"
        if self.mode in TEXT_MODES:
            if st.get("status") == "error":
                return "正確版在你的帳本裡跑不起來，先確定 0-5 的環境檢查都過了（uv run check.py env）。"
            if not c.line:
                n = st.get("got_n", 0)
                body_n = int(re.sub(r"\D", "", c.text) or 0)
                more = "多" if body_n > n else "少"
                return (f"正確版一共印出 {n} 行，你寫了 {body_n} 行（{more}了 {abs(body_n - n)} 行）。\n"
                        "  看看是不是多了或少了一行：空白的一行也算一行。")
            shown = c.text if c.text.strip() else "（空白的一行）"
            if st.get("why") == "missing":
                return f"第 {c.line} 行「{shown}」：正確版沒有印到這一行，你寫的比它多。"
            return (f"第 {c.line} 行「{shown}」跟正確版印出來的不一樣。\n"
                    "  一個字一個字對：空格、標點、空白的一行都要一樣（全形、半形的冒號都可以）。")
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
        n_count = len([c for c in checks if c.line]) if self.mode in TEXT_MODES else n   # expected_text：總行數那一條不算
        count_r.ok = n_count >= self.min
        if not count_r.ok:
            extra = f"（還有 {unfinished} 行有「？」沒填完）" if unfinished else ""
            marked = "；行尾標了特殊作答的不算在裡面" if marks else ""
            if self.mode in TEXT_MODES:
                count_r.detail = f"你的預期輸出寫了 {n_count} 行，這課要至少 {self.min} 行{extra}。"
            elif self.mode == "cases":
                marked = "；標了「已知會當掉」的不算在裡面" if marks else ""
                count_r.detail = f"你寫了 {n} 組案例，這課要至少 {self.min} 組{extra}{marked}。"
            else:
                count_r.detail = (f"你寫了 {n} 件事，這課要至少 {self.min} 件{extra}。" if self.mode == "table_facts"
                                  else f"你寫了 {n} 條檢查，這課要至少 {self.min} 條{extra}{marked}。")
        reveal = count_r.ok  # 寫滿最少條數以前，先不講溜過去的是哪一種錯

        mark_status: dict[int, dict] = {}
        if n or (marks and self.mode in ("assert", "cases")):
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
                    if self.mode in TEXT_MODES:
                        r.note = f"被第 {checks[first].line} 行抓到" if checks[first].line else "被「總行數」抓到（印出來的行數不一樣）"
                        if rows[first].get("crashed"):
                            r.note += "（這個版本跑到一半當掉了）"
                    else:
                        r.note = f"被第 {checks[first].line} 行抓到"
                    if rows[first].get("stuck"):
                        r.note += "（這個壞版本卡住了、跑不完，你的檢查抓到它）"
                elif not valid:
                    r.detail = "你的檢查在正確版上還沒有一條成立，先修好正確版那一題。"
                    slipped.append(m["hint"])
                else:
                    unit = {"expected_text": "行", "inputs_text": "行", "cases": "組案例", "table_facts": "件事"}.get(self.mode, "條檢查")
                    r.detail = f"溜過去了：{m['hint']}" if reveal else f"溜過去了。（先寫滿 {self.min} {unit}，再告訴你溜過去的是哪一種錯）"
                    slipped.append(m["hint"])
            caught = len(self.mutants) - len(slipped)
            stuck_caught = [k for k, r in enumerate(mutant_rs, start=1) if r.ok and f"m{k}" in self._stuck_names]
            stuck_lines = ([f"  其中 {len(stuck_caught)} 個卡在迴圈裡停不下來：",   # 1-10：看得到 check 的逾時（每行 ≤68 欄）
                            f"  check 等了 {self.version_timeout():.0f} 秒，把它停下來，算你抓到。"]
                           if stuck_caught and self.spec.get("stuck_note") else [])
            # 1-11 修：1-10 把 stuck_note 那段插在 if not slipped 和 elif reveal 中間，全部抓到時又多印一行「抓到 3 個壞版本，還有 0 個溜過去：」；
            # 改回原本的三選一，逾時那兩行接在後面（1-10 兩種情況印出來的字跟原本一樣）
            if not slipped:
                self.ctx.summaries.append(f"你的{CHAFF_NOUN.get(self.mode, '檢查')}把 {len(self.mutants)} 個壞版本全部抓到了。")
                self.ctx.summaries.extend(stuck_lines)
            elif reveal:
                # 每行壓在 68 欄內（VHS 錄影 70 欄、Terminal.app 預設 80 欄都不折行）：提示一條一行
                self.ctx.summaries.append(f"你的{CHAFF_NOUN.get(self.mode, '檢查')}抓到 {caught} 個壞版本，還有 {len(slipped)} 個溜過去：")
                self.ctx.summaries.extend(f"  ・{h}" for h in slipped)
            else:
                # 分兩行（每行 ≤68 欄，同上）
                noun, unit = {"expected_text": ("預期輸出", "行"), "inputs_text": ("預期輸出", "行"), "cases": ("案例", "組案例"), "table_facts": ("檢查", "件事")}.get(self.mode, ("檢查", "條檢查"))
                self.ctx.summaries.append(f"你的{noun}抓到 {caught} 個壞版本，還有 {len(slipped)} 個溜過去。")
                self.ctx.summaries.append(f"  先寫滿 {self.min} {unit}，再告訴你是哪幾種。")
        else:
            none = {"expected_text": "還沒寫預期輸出", "inputs_text": "還沒寫預期輸出", "cases": "還沒有任何案例", "table_facts": "還沒寫任何一件事（「？」還沒改）"}.get(self.mode, "還沒有任何檢查")
            wheat_r.detail = f"{none}。" + (f"（有 {unfinished} 行的「？」還沒填）" if unfinished else "")
            for r in mutant_rs:
                r.detail = f"{none}，所以壞版本都溜過去了。"

        if marks:
            key = json.loads(self.ctx.course(self.spec["special"]).read_text(encoding="utf-8")) if self.spec.get("special") else {"rules": []}
            for mk in marks:
                r = by_id[f"s{mk.line}"]
                if self.mode == "cases":
                    r.ok, r.detail, r.note = judge_case_mark(mk, self._cases[mk.line][0], self.spec["func"], key, mark_status.get(mk.line, {}))
                else:
                    r.ok, r.detail, r.note = judge_mark(mk, key, mark_status.get(mk.line, {}))
        if "smin" in by_id:
            by_id["smin"].detail = ("還沒有一組標「已知會當掉」：找一個連正確版都轉不了的金額，\n"
                                    "  在那一行最後加上「# 已知會當掉」（右邊可以不寫）。")


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


def judge_case_mark(mk: Mark, inp, func: str, key: dict, ref: dict) -> tuple[bool, str, str]:
    """cases 的特殊作答：「已知會當掉」看正確版真的跑這個輸入會不會當掉；「需求有問題」照 special.json 的 match（正規式比對輸入）。"""
    call = f"{func}({typed(inp, bare=True)})"
    crashed = ref.get("status") == "error" and not ref.get("stuck")
    rules = [r for r in key.get("rules", []) if isinstance(inp, str) and re.search(r.get("match", "(?!)"), inp)]
    if mk.kind == "已知會當掉":
        if crashed:
            explain = next((r["explain"] for r in rules if r["kind"] == "已知會當掉"), key.get("crash_explain", ""))
            return True, "", f"{call}：正確版真的會當掉（{ref.get('error')}）。" + explain
        if ref.get("stuck"):
            return False, f"第 {mk.line} 行標了「已知會當掉」，可是正確版跑 {call} 是卡住（{ref.get('error')}），不是當掉。", ""
        got = typed(ref.get("got"), ref.get("got_type"))
        return False, (f"第 {mk.line} 行標了「已知會當掉」，可是正確版轉得出來：{call} 變成 {got}。"
                       "\n  換一個連正確版都轉不了的金額；或拿掉標記，當成一般的案例。"), ""
    if crashed:
        return False, (f"第 {mk.line} 行標了「需求有問題」，方向對了一半：正確版跑 {call} 會當掉（{ref.get('error')}），"
                       "這比較像「已知會當掉」。"), ""
    for rule in rules:
        if rule["kind"] == "需求有問題":
            return True, "", f"{call}：{rule['explain']}"
    return False, (f"第 {mk.line} 行標了「需求有問題」，可是 {call} 的需求講得很清楚。"
                   "\n  把標記拿掉，當成一般的案例就好。"), ""


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
                # 一行寫得完（終端機 70 欄、Git Bash 80 欄不折行；0-C 影片錄到這一行）
                r.detail = f"{rel} 改過之後還沒按存檔點。到原始碼控制面板按存檔點（commit）。"
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
    "parsons": ParsonsCheck,
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
