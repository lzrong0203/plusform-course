# /// script
# requires-python = ">=3.13"
# ///
"""看得懂進度條：替 showcase 帳本的每一行標上概念。

用 Python 內建的 ast 模組（它會把程式拆成一個一個零件）讀 showcase/ledger_app.py，
每一行標上用到的概念（變數、print、if、for、dict、函式、class……）。
再對照你已經通過的課，算出這支程式你「看得懂」幾成。

用法（在課程資料夾裡打）：
    uv run concept_map.py                 照你帳本裡的進度算
    uv run concept_map.py --lines         每一行都列出來，看哪幾行還看不懂
    uv run concept_map.py --upto 1-11     假設學到 1-11（含）為止，算算看
    uv run concept_map.py --passed 1-1,1-2,1-9
    uv run concept_map.py --json          給程式讀的格式

這是粗略的判斷：只看程式長什麼樣子，不真的執行。只用 Python 標準庫。
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 13) and __name__ == "__main__":  # 舊版 Python（例如 Mac 內建的 3.9）也看得懂這段
    print("concept_map.py 要用 Python 3.13 跑。請在課程資料夾裡打：uv run concept_map.py（不要用 python3）")
    sys.exit(2)

sys.dont_write_bytecode = True  # 課程資料夾裡什麼都不寫（連 __pycache__ 也不要）

import argparse  # noqa: E402
import ast  # noqa: E402
import io
import json
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHOWCASE = ROOT / "showcase" / "ledger_app.py"

# 概念代號：(畫面上的名字, 教這個概念的課)
CONCEPTS: dict[str, tuple[str, str | None]] = {
    "comment": ("註解", "1-1"),
    "print": ("print", "1-1"),
    "variable": ("變數", "1-2"),
    "types": ("資料型別", "1-3"),
    "math": ("數字運算", "1-4"),
    "string": ("字串操作", "1-5"),
    "input": ("input", "1-6"),
    "call": ("函式呼叫", "1-6"),
    "logic": ("比較與邏輯", "1-8"),
    "if": ("if", "1-9"),
    "while": ("while", "1-10"),
    "for": ("for", "1-11"),
    "list": ("list", "1-13"),
    "tuple_set": ("tuple 與 set", "1-14"),
    "dict": ("dict", "1-15"),
    "comprehension": ("推導式與 zip", "1-17"),
    "def": ("函式定義", "1-18"),
    "params": ("預設值與關鍵字參數", "1-19"),
    "hints": ("型別提示與 lambda", "1-20"),
    "import": ("模組與 import", "1-21"),
    "exception": ("例外處理", "1-22"),
    "file": ("檔案讀寫", "1-23"),
    "class": ("class", "1-24"),
    # Lv2 才教的模組：不要混進「模組與 import」，不然 Lv1 的進度條會假裝看得懂
    "json": ("CSV 與 JSON", "2-4"),
    "sqlite": ("SQLite", "2-5"),
    "http": ("呼叫網路 API", "2-6"),
    "environ": ("環境變數", "2-7"),
    "unknown": ("課程沒教的寫法", None),
}

# 模組名稱（或「模組.名稱」）→ 概念。沒列的模組照「模組與 import」（1-21）算。
MODULE_TOPICS = {
    "json": "json", "csv": "json", "sqlite3": "sqlite", "httpx": "http", "requests": "http",
    "urllib": "http", "dotenv": "environ", "os.environ": "environ", "os.getenv": "environ",
    "os.putenv": "environ", "environ": "environ", "getenv": "environ",
}

# CONCEPTS.md 裡可以用的別名
ALIASES = {
    "註解": "comment", "print": "print", "變數": "variable", "資料型別": "types", "型別": "types",
    "數字運算": "math", "運算": "math", "字串操作": "string", "字串": "string", "f-string": "string",
    "input": "input", "函式呼叫": "call", "型別轉換": "call", "比較與邏輯": "logic", "比較": "logic",
    "邏輯": "logic", "assert": "logic", "if": "if", "elif": "if", "else": "if", "while": "while",
    "for": "for", "range": "for", "enumerate": "for", "list": "list", "tuple 與 set": "tuple_set",
    "tuple": "tuple_set", "set": "tuple_set", "dict": "dict", "推導式與 zip": "comprehension",
    "推導式": "comprehension", "zip": "comprehension", "函式定義": "def", "函式外殼": "def", "def": "def",
    "return": "def", "預設值與關鍵字參數": "params", "關鍵字參數": "params", "型別提示與 lambda": "hints",
    "型別提示": "hints", "lambda": "hints", "模組與 import": "import", "模組": "import", "import": "import",
    "例外處理": "exception", "例外": "exception", "檔案讀寫": "file", "檔案": "file", "class": "class",
    "類別": "class", "CSV 與 JSON": "json", "JSON": "json", "CSV": "json", "SQLite": "sqlite",
    "呼叫網路 API": "http", "環境變數": "environ",
}

STR_METHODS = {
    "strip", "lstrip", "rstrip", "split", "rsplit", "replace", "startswith", "endswith", "join", "upper",
    "lower", "title", "isdigit", "isnumeric", "isalpha", "ljust", "rjust", "center", "format", "find",
    "zfill", "removeprefix", "removesuffix", "splitlines", "count",
}
LIST_METHODS = {"append", "insert", "remove", "pop", "sort", "extend", "index", "reverse", "clear", "copy"}
DICT_METHODS = {"get", "items", "keys", "values", "setdefault", "update"}
FILE_METHODS = {"read", "write", "readline", "readlines", "exists", "mkdir", "read_text", "write_text",
                "is_file", "is_dir", "glob", "iterdir", "open", "home", "cwd"}
NAME_CALLS = {
    "print": "print", "input": "input", "range": "for", "enumerate": "for", "zip": "comprehension",
    "sorted": "list", "sum": "list", "min": "list", "max": "list", "list": "list", "dict": "dict",
    "set": "tuple_set", "tuple": "tuple_set", "open": "file", "any": "hints", "all": "hints",
}
UNKNOWN_NODES = (ast.Yield, ast.YieldFrom, ast.Await, ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith,
                 ast.Match, ast.NamedExpr, ast.TryStar)


def _root_name(node: ast.AST) -> str | None:
    """a.b.c 這種一串的，找出最前面的名字 a。"""
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _root_any(node: ast.AST) -> str | None:
    """a.b().c 這種中間夾著呼叫的，也找出最前面的名字 a。"""
    while isinstance(node, (ast.Attribute, ast.Call, ast.Subscript)):
        node = node.func if isinstance(node, ast.Call) else node.value
    return node.id if isinstance(node, ast.Name) else None


def _dotted(node: ast.AST) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def name_to_key(name: str) -> str | None:
    text = name.strip().strip("`").strip()
    if text in CONCEPTS:
        return text
    if text in ALIASES:
        return ALIASES[text]
    for key, (label, _lesson) in CONCEPTS.items():
        if label == text:
            return key
    return None


@dataclass
class LineInfo:
    lineno: int
    text: str
    concepts: set[str] = field(default_factory=set)


class _Tagger:
    def __init__(self, tree: ast.AST):
        self.tags: dict[int, set[str]] = {}
        self.spans: list[tuple[int, int, set[str]]] = []
        self.imported: set[str] = set()
        self.origin: dict[str, str] = {}  # 匯入的名字 → 從哪個模組來（json、os.environ…）
        self.classes: set[str] = set()
        self.skip: set[int] = set()  # 不另外標的節點（型別提示裡面、函式名稱）
        self.docstring_lines: set[int] = set()
        self.parents: dict[int, ast.AST] = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                self.parents[id(child)] = node
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = (alias.asname or alias.name).split(".")[0]
                    self.imported.add(name)
                    self.origin[name] = alias.name.split(".")[0]
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    self.imported.add(name)
                    self.origin[name] = f"{(node.module or '').split('.')[0]}.{alias.name}"
            elif isinstance(node, ast.ClassDef):
                self.classes.add(node.name)
        self._mark_annotations_and_docstrings(tree)

    def _skip_subtree(self, node: ast.AST) -> None:
        for sub in ast.walk(node):
            self.skip.add(id(sub))

    def _mark_annotations_and_docstrings(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                body = node.body
                if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                        and isinstance(body[0].value.value, str):
                    doc = body[0]
                    self._skip_subtree(doc)
                    self.docstring_lines.update(range(doc.lineno, (doc.end_lineno or doc.lineno) + 1))
            annotations = []
            if isinstance(node, ast.arg) and node.annotation is not None:
                annotations.append(node.annotation)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns is not None:
                annotations.append(node.returns)
            if isinstance(node, ast.AnnAssign):
                annotations.append(node.annotation)
            for ann in annotations:
                self._skip_subtree(ann)
                self.add(ann.lineno, {"hints"}, ann)

    def add(self, line: int, concepts: set[str], node: ast.AST | None = None) -> None:
        if not concepts:
            return
        self.tags.setdefault(line, set()).update(concepts)
        if node is not None and getattr(node, "end_lineno", None):
            self.spans.append((node.lineno, node.end_lineno, set(concepts)))

    # ---------- 每一種零件對應的概念 ----------
    def concepts_for(self, node: ast.AST) -> set[str]:
        parent = self.parents.get(id(node))
        c: set[str] = set()
        if isinstance(node, UNKNOWN_NODES):
            return {"unknown"}
        if isinstance(node, ast.Call):
            c |= self._call(node)
        elif isinstance(node, ast.Name):
            if isinstance(parent, ast.Call) and parent.func is node:
                return set()
            if node.id == "self":
                c.add("class")
            elif node.id == "__name__":
                c.add("import")
            elif node.id in self.imported and isinstance(node.ctx, ast.Load):
                c.add(self.module_topic(node))
            elif node.id == "Exception" or node.id.endswith("Error"):
                c.add("exception")
            else:
                c.add("variable")
        elif isinstance(node, ast.Attribute):
            if isinstance(parent, ast.Call) and parent.func is node:
                return set()
            if _root_name(node) in self.imported:
                c.add(self.module_topic(node))
            else:
                c.add("class")
        elif isinstance(node, ast.Constant):
            if node.value is not Ellipsis:
                c.add("types")
        elif isinstance(node, (ast.JoinedStr, ast.FormattedValue)):
            c.add("string")
        elif isinstance(node, ast.Subscript):
            if isinstance(node.slice, ast.Slice):
                c.add("string")
            elif isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                c.add("dict")
            else:
                c.add("list")
        elif isinstance(node, ast.Slice):
            c.add("string")
        elif isinstance(node, ast.BinOp):
            c.add("math")
        elif isinstance(node, ast.UnaryOp):
            c.add("logic" if isinstance(node.op, ast.Not) else "math")
        elif isinstance(node, (ast.BoolOp, ast.Compare, ast.Assert)):
            c.add("logic")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            c.add("variable")
        elif isinstance(node, ast.AugAssign):
            c |= {"variable", "math"}
        elif isinstance(node, (ast.If, ast.IfExp)):
            c.add("if")
        elif isinstance(node, (ast.While, ast.Break, ast.Continue)):
            c.add("while")
        elif isinstance(node, ast.For):
            c.add("for")
        elif isinstance(node, ast.List):
            c.add("list")
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            c.add("comprehension")
        elif isinstance(node, ast.Tuple):
            if isinstance(parent, (ast.For, ast.comprehension)) and parent.target is node:
                c.add("for")
            else:
                c.add("tuple_set")
        elif isinstance(node, ast.Set):
            c.add("tuple_set")
        elif isinstance(node, ast.Starred):
            c.add("hints" if isinstance(parent, ast.Call) else "tuple_set")
        elif isinstance(node, ast.Dict):
            c.add("dict")
            if any(k is None for k in node.keys):
                c.add("hints")
        elif isinstance(node, ast.FunctionDef):
            c.add("def")
            if isinstance(parent, ast.ClassDef):
                c.add("class")
            if node.args.defaults or node.args.kw_defaults:
                c.add("params")
            if node.args.vararg or node.args.kwarg:
                c.add("hints")
            for deco in node.decorator_list:
                self.add(deco.lineno, {"class"} if isinstance(parent, ast.ClassDef) else {"def"}, deco)
        elif isinstance(node, ast.arg):
            c.add("class" if node.arg == "self" else "def")
        elif isinstance(node, ast.Return):
            c.add("def")
        elif isinstance(node, ast.Lambda):
            c.add("hints")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            c.add("import")
            for alias in node.names:
                base = node.module if isinstance(node, ast.ImportFrom) else alias.name
                base = (base or "").split(".")[0]
                for key in (f"{base}.{alias.name}", base):
                    if key in MODULE_TOPICS:
                        c.add(MODULE_TOPICS[key])
                        break
        elif isinstance(node, ast.alias):
            c.add("import")
        elif isinstance(node, (ast.Try, ast.ExceptHandler, ast.Raise)):
            c.add("exception")
        elif isinstance(node, ast.With):
            c.add("file")
        elif isinstance(node, ast.ClassDef):
            c.add("class")
            for deco in node.decorator_list:
                self.add(deco.lineno, {"class"}, deco)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            c.add("params")
        elif isinstance(node, ast.Delete):
            c.add("list")
        return c

    def _call(self, node: ast.Call) -> set[str]:
        c: set[str] = set()
        func = node.func
        fname = None
        if isinstance(func, ast.Name):
            fname = func.id
            if fname in NAME_CALLS:
                c.add(NAME_CALLS[fname])
            elif fname in self.classes:
                c.add("class")
            elif fname in self.imported:
                c.add(self.module_topic(func))
            else:
                c.add("call")
        elif isinstance(func, ast.Attribute):
            fname = func.attr
            if _root_any(func.value) in self.imported:
                c.add(self.module_topic(func))
            elif isinstance(func.value, ast.Name) and func.value.id == "self":
                c.add("class")
            elif fname in STR_METHODS:
                c.add("string")
            elif fname in LIST_METHODS:
                c.add("list")
            elif fname in DICT_METHODS:
                c.add("dict")
            elif fname in FILE_METHODS:
                c.add("file")
            else:
                c.add("class")  # 物件自己的方法（ledger.total()）：1-24 才教
        else:
            c.add("call")
        for kw in node.keywords:
            if kw.arg is None:
                c.add("hints")
            elif fname == "print" and kw.arg in ("sep", "end"):
                c.add("print")
            elif kw.arg in ("key", "reverse") and fname in ("sorted", "sort", "max", "min"):
                c.add("hints")
            elif kw.arg in ("encoding", "mode", "newline"):
                c.add("file")
            elif kw.arg == "start" and fname == "enumerate":
                c.add("for")
            else:
                c.add("params")
        return c

    def module_topic(self, node: ast.AST) -> str:
        """匯入的模組屬於哪一課：json、os.environ 這些 Lv2 才教，其他照 1-21 的「模組與 import」。"""
        root = _root_any(node)
        origin = self.origin.get(root or "", root or "")
        dotted = _dotted(node.func if isinstance(node, ast.Call) else node)
        full = origin + dotted[len(root or ""):] if root and dotted.startswith(root) else origin
        for key in (full, ".".join(full.split(".")[:2]), origin, origin.split(".")[0]):
            if key in MODULE_TOPICS:
                return MODULE_TOPICS[key]
        return "import"

    def run(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if id(node) in self.skip or not hasattr(node, "lineno"):
                continue
            concepts = self.concepts_for(node)
            self.add(node.lineno, concepts, node)


def analyze_source(source: str) -> list[LineInfo]:
    """回傳每一行（含空行）的概念。空行的 concepts 是空集合。"""
    tree = ast.parse(source)
    tagger = _Tagger(tree)
    tagger.run(tree)
    lines = source.splitlines()
    comment_lines: set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT:
                comment_lines.add(tok.start[0])
    except tokenize.TokenError:
        pass
    out = []
    for i, text in enumerate(lines, start=1):
        info = LineInfo(i, text)
        stripped = text.strip()
        if not stripped:
            out.append(info)
            continue
        if i in tagger.docstring_lines:
            info.concepts = {"comment"}
        elif stripped.startswith("#") and i in comment_lines:
            info.concepts = {"comment"}
        elif i in tagger.tags:
            info.concepts = set(tagger.tags[i])
        else:
            covering = [s for s in tagger.spans if s[0] <= i <= s[1]]
            if covering:
                best = min(covering, key=lambda s: s[1] - s[0])
                info.concepts = set(best[2])
            else:
                info.concepts = {"unknown"}
        out.append(info)
    return out


def concepts_in_source(source: str) -> set[str]:
    out: set[str] = set()
    for info in analyze_source(source):
        out |= info.concepts
    return out


def lesson_concepts(lessons: set[str]) -> set[str]:
    return {key for key, (_label, lesson) in CONCEPTS.items() if lesson and lesson in lessons}


@dataclass
class Progress:
    understood: int
    total: int
    lines: list[LineInfo]
    known: set[str]
    next_lesson: str | None = None
    next_gain: int = 0

    @property
    def percent(self) -> int:
        return round(self.understood * 100 / self.total) if self.total else 0


def progress(source: str, lessons: set[str]) -> Progress:
    lines = analyze_source(source)
    code = [ln for ln in lines if ln.text.strip()]
    known = lesson_concepts(lessons)
    understood = sum(1 for ln in code if ln.concepts <= known)
    prog = Progress(understood=understood, total=len(code), lines=lines, known=known)
    best_gain, best_lesson = 0, None
    order = [lesson for _label, lesson in CONCEPTS.values() if lesson]
    for lesson in dict.fromkeys(order):
        if lesson in lessons:
            continue
        more = known | lesson_concepts({lesson})
        gain = sum(1 for ln in code if ln.concepts <= more) - understood
        if gain > best_gain:
            best_gain, best_lesson = gain, lesson
    prog.next_lesson, prog.next_gain = best_lesson, best_gain
    return prog


def bar(percent: int, width: int = 20) -> str:
    filled = round(percent * width / 100)
    return "█" * filled + "░" * (width - filled)


def lessons_upto(upto: str) -> set[str]:
    course = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
    order = [x["id"] for x in course["lessons"]]
    if upto not in order:
        raise SystemExit(f"課程裡沒有 {upto} 這一課。")
    return set(order[: order.index(upto) + 1])


def passed_from_ledger() -> set[str] | None:
    try:
        from engine import state
    except ImportError:
        return None
    ledger = state.ledger_from_config()
    if ledger is None:
        return None
    lessons = state.Records(ledger).progress().get("lessons", {})
    return {lid for lid, info in lessons.items() if info.get("first_pass")}


def label(key: str) -> str:
    return CONCEPTS.get(key, (key, None))[0]


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(description="看得懂進度條：替帳本程式的每一行標上概念。")
    p.add_argument("file", nargs="?", default=str(SHOWCASE), help="要分析的 .py 檔（預設是 showcase 帳本）")
    p.add_argument("--passed", help="已經通過的課，用逗號隔開，例如 1-1,1-2,1-9")
    p.add_argument("--upto", help="假設學到這一課（含）為止")
    p.add_argument("--lines", action="store_true", help="每一行都列出來")
    p.add_argument("--json", action="store_true", help="輸出 JSON")
    args = p.parse_args(argv)

    if args.passed:
        lessons = {x.strip() for x in args.passed.split(",") if x.strip()}
        source_note = "照你指定的課"
    elif args.upto:
        lessons = lessons_upto(args.upto)
        source_note = f"假設學到 {args.upto} 為止"
    else:
        found = passed_from_ledger()
        lessons = found or set()
        source_note = "照你帳本裡通過的課" if found is not None else "還沒設定帳本，先當作一課都還沒過"

    path = Path(args.file)
    prog = progress(path.read_text(encoding="utf-8"), lessons)

    if args.json:
        print(json.dumps({
            "file": str(path),
            "percent": prog.percent,
            "understood": prog.understood,
            "total": prog.total,
            "next_lesson": prog.next_lesson,
            "next_gain": prog.next_gain,
            "lines": [{"line": ln.lineno, "concepts": sorted(ln.concepts),
                       "ok": ln.concepts <= prog.known} for ln in prog.lines if ln.text.strip()],
        }, ensure_ascii=False, indent=2))
        return 0

    if args.lines:
        for ln in prog.lines:
            if not ln.text.strip():
                print(f"{ln.lineno:>4}    │")
                continue
            mark = "✓" if ln.concepts <= prog.known else "·"
            names = "、".join(label(k) for k in sorted(ln.concepts, key=list(CONCEPTS).index))
            print(f"{ln.lineno:>4} {mark}  │ {ln.text:<70} ［{names}］")
        print()

    print(f"看得懂進度條：[{bar(prog.percent)}] {prog.percent}%（{source_note}）")
    print(f"{path.name} 一共 {prog.total} 行（不算空行），你看得懂 {prog.understood} 行。")
    if prog.next_lesson:
        print(f"下一步：學完 {prog.next_lesson}，可以多看懂 {prog.next_gain} 行。")
    elif prog.understood == prog.total:
        print("整支程式你都看得懂了！")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
