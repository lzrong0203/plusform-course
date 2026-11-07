"""假的終端機：在記憶體裡模擬幾個建資料夾的指令，不碰真的檔案。

用在 0-4 和 0-C 的第③圈：學員寫「跑完之後應該要有什麼」，check.py 拿正確版
和壞版本的腳本在這個假的資料夾裡各跑一次，看學員的檢查抓不抓得到。
壞版本裡有 rm -rf，所以絕對不能真的跑，只在這裡模擬。

支援：cd、mkdir [-p]、touch、cp [-r]、mv、rm [-r] [-f]、echo、ls、pwd、cat、
註解（#）、以及用 ; 或 && 串起來的指令。萬用字元 * ? 只比對同一層。

模擬不了的寫法（$變數、$(…)、反引號、> 和 < 重新導向、{a,b} 大括號展開、[ ]、~別人）
一律記成錯誤（fail closed）：寧可說「沒辦法保證安全」，也不能把真的 bash 會刪東西的腳本說成安全。
只用 Python 標準庫。
"""

from __future__ import annotations

import fnmatch
import posixpath
import shlex
from dataclasses import dataclass, field

DIR = "d"
FILE = "f"


@dataclass
class VResult:
    fs: dict[str, str]
    errors: list[tuple[int, str]] = field(default_factory=list)
    cwd: str = "/"
    home: str = "/"


class _Shell:
    def __init__(self, home: str, cwd: str, start: list[str]):
        self.home = posixpath.normpath(home)
        self.cwd = posixpath.normpath(cwd)
        self.fs: dict[str, str] = {"/": DIR}
        self.errors: list[tuple[int, str]] = []
        self._mkdirs(self.home)
        self._mkdirs(self.cwd)
        for item in start:
            item = item.strip()
            if not item or item.startswith("#"):
                continue
            path = self.abs(item)
            if item.endswith("/"):
                self._mkdirs(path)
            else:
                self._mkdirs(posixpath.dirname(path))
                self.fs[path] = FILE

    # ---------- 路徑 ----------
    def abs(self, p: str) -> str:
        if p == "~" or p.startswith("~/"):
            p = self.home + p[1:]
        if not p.startswith("/"):
            p = posixpath.join(self.cwd, p)
        p = posixpath.normpath(p)
        if p.startswith("//"):
            p = p[1:]
        return p

    def _mkdirs(self, path: str) -> None:
        parts = [x for x in path.split("/") if x]
        cur = ""
        for part in parts:
            cur += "/" + part
            self.fs[cur] = DIR

    def _children(self, path: str) -> list[str]:
        prefix = path.rstrip("/") + "/"
        return [p for p in self.fs if p.startswith(prefix) and p != path]

    def _subtree(self, path: str) -> list[str]:
        return [path] + self._children(path)

    def _err(self, line: int, msg: str) -> bool:
        self.errors.append((line, msg))
        return False

    def _expand(self, args: list[str]) -> list[str]:
        out: list[str] = []
        for a in args:
            if "*" in a or "?" in a:
                parent = posixpath.dirname(a) or "."
                pattern = posixpath.basename(a)
                parent_abs = self.abs(parent)
                names = sorted(
                    posixpath.basename(p)
                    for p in self.fs
                    if posixpath.dirname(p) == parent_abs and p != parent_abs
                )
                hits = [n for n in names if not n.startswith(".") and fnmatch.fnmatchcase(n, pattern)]
                if hits:
                    out.extend(posixpath.join(parent, n) if parent != "." else n for n in hits)
                    continue
            out.append(a)
        return out

    # ---------- 指令 ----------
    def run_command(self, line: int, words: list[str]) -> bool:
        if not words:
            return True
        cmd, args = words[0], self._expand(words[1:])
        flags = {a for a in args if a.startswith("-") and len(a) > 1}
        paths = [a for a in args if not (a.startswith("-") and len(a) > 1)]
        letters = set("".join(f.lstrip("-") for f in flags))

        if cmd in ("echo", "ls", "pwd", "cat", "true", "clear"):
            return True
        if cmd == "cd":
            target = self.abs(paths[0]) if paths else self.home
            if self.fs.get(target) != DIR:
                return self._err(line, f"cd: no such file or directory: {paths[0] if paths else '~'}")
            self.cwd = target
            return True
        if cmd == "mkdir":
            ok = True
            for p in paths:
                path = self.abs(p)
                if "p" in letters:
                    if self.fs.get(path) == FILE:
                        ok = self._err(line, f"mkdir: {p}: File exists")
                    else:
                        self._mkdirs(path)
                    continue
                if path in self.fs:
                    ok = self._err(line, f"mkdir: {p}: File exists")
                elif self.fs.get(posixpath.dirname(path)) != DIR:
                    ok = self._err(line, f"mkdir: {p}: No such file or directory")
                else:
                    self.fs[path] = DIR
            return ok
        if cmd == "touch":
            ok = True
            for p in paths:
                path = self.abs(p)
                if path in self.fs:
                    continue
                if self.fs.get(posixpath.dirname(path)) != DIR:
                    ok = self._err(line, f"touch: {p}: No such file or directory")
                else:
                    self.fs[path] = FILE
            return ok
        if cmd in ("cp", "mv"):
            if len(paths) < 2:
                return self._err(line, f"{cmd}: 少了來源或目的地")
            *sources, dest = paths
            ok = True
            for src in sources:
                ok = self._copy_or_move(line, cmd, src, dest, recursive=bool(letters & {"r", "R"})) and ok
            return ok
        if cmd == "rm":
            ok = True
            recursive = bool(letters & {"r", "R"})
            force = "f" in letters
            for p in paths:
                if posixpath.basename(p.rstrip("/")) in (".", ".."):
                    ok = self._err(line, 'rm: "." and ".." may not be removed')
                    continue
                path = self.abs(p)
                kind = self.fs.get(path)
                if kind is None:
                    if not force:
                        ok = self._err(line, f"rm: {p}: No such file or directory")
                    continue
                if path == "/":
                    ok = self._err(line, "rm: 拒絕刪除根目錄")
                    continue
                if kind == DIR and not recursive:
                    ok = self._err(line, f"rm: {p}: is a directory")
                    continue
                for q in self._subtree(path):
                    self.fs.pop(q, None)
            return ok
        return self._err(line, f"{cmd}: command not found")

    def _copy_or_move(self, line: int, cmd: str, src: str, dest: str, recursive: bool) -> bool:
        s = self.abs(src)
        d = self.abs(dest)
        kind = self.fs.get(s)
        if kind is None:
            return self._err(line, f"{cmd}: {src}: No such file or directory")
        if kind == DIR and cmd == "cp" and not recursive:
            return self._err(line, f"cp: {src} is a directory (not copied).")
        if self.fs.get(d) == DIR:
            d = posixpath.join(d, posixpath.basename(s))
        elif self.fs.get(posixpath.dirname(d)) != DIR:
            return self._err(line, f"{cmd}: {dest}: No such file or directory")
        if d == s or d.startswith(s.rstrip("/") + "/"):
            return self._err(line, f"{cmd}: 不能把資料夾放進它自己裡面")
        moved = {q: self.fs[q] for q in self._subtree(s)}
        if cmd == "mv":
            for q in moved:
                self.fs.pop(q, None)
        for q, k in moved.items():
            self.fs[d + q[len(s):]] = k
        return True


UNSUPPORTED_HELP = "沒辦法保證安全。這一關只用 0-4 教過的指令和一般的路徑，不要用 $、`、>、<、{a,b} 這些寫法。"


def _snippet(line: str, i: int) -> str:
    j = i + 1
    while j < len(line) and line[j] not in " \t;&|'\"/":
        j += 1
    return line[i:j] or line[i]


def unsupported(line: str) -> str | None:
    """找出這一行裡模擬器看不懂的寫法，回傳那一段（看得懂就回傳 None）。"""
    quote = None
    word_start = True
    i, n = 0, len(line)
    while i < n:
        ch = line[i]
        if quote == "'":
            if ch == "'":
                quote = None
            i += 1
            continue
        if ch == "\\":
            i += 2
            word_start = False
            continue
        if quote == '"':
            if ch == '"':
                quote = None
            elif ch in "$`":
                return _snippet(line, i)
            i += 1
            continue
        if ch == "#" and word_start:
            break
        if ch in "'\"":
            quote = ch
            word_start = False
        elif ch in "$`":
            return _snippet(line, i)
        elif ch in "<>":
            return ch
        elif ch == "{":
            end = line.find("}", i)
            if end > i and ("," in line[i:end] or ".." in line[i:end]):
                return line[i:end + 1]
            word_start = False
        elif ch in "[]":
            return _snippet(line, i)
        elif ch == "~" and word_start and i + 1 < n and line[i + 1] not in " \t/;&|":
            return _snippet(line, i)
        elif ch in " \t;&|":
            word_start = True
        else:
            word_start = False
        i += 1
    return None


def _split_commands(text: str) -> list[tuple[str, list[str]]]:
    """把一行拆成 [(連接詞, 字詞)]，連接詞是 ';' 或 '&&'。"""
    lex = shlex.shlex(text, posix=True, punctuation_chars=";&|")
    lex.whitespace_split = True
    lex.commenters = "#"
    out: list[tuple[str, list[str]]] = []
    joiner = ";"
    words: list[str] = []
    for tok in lex:
        if tok in (";", "&&", "&", "||", "|"):
            out.append((joiner, words))
            joiner = "&&" if tok == "&&" else ";"
            words = []
        else:
            words.append(tok)
    out.append((joiner, words))
    return out


def run(script: str, home: str, cwd: str, start: list[str] | None = None) -> VResult:
    """模擬跑一段腳本，回傳跑完之後的假資料夾。"""
    sh = _Shell(home, cwd, start or [])
    for lineno, raw in enumerate(script.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        odd = unsupported(stripped)
        if odd:
            sh._err(lineno, f"有模擬器看不懂的寫法（{odd}），{UNSUPPORTED_HELP}")
            continue
        try:
            parts = _split_commands(stripped)
        except ValueError as exc:  # 引號沒關好
            sh._err(lineno, f"這一行看不懂：{exc}")
            continue
        last_ok = True
        for joiner, words in parts:
            if joiner == "&&" and not last_ok:
                continue
            last_ok = sh.run_command(lineno, words)
    return VResult(fs=dict(sh.fs), errors=sh.errors, cwd=sh.cwd, home=sh.home)


def resolve(result: VResult, base_cwd: str, path: str) -> str:
    """把學員寫的相對路徑換成假資料夾裡的絕對路徑。"""
    p = path.strip()
    if p == "~" or p.startswith("~/"):
        p = result.home + p[1:]
    if not p.startswith("/"):
        p = posixpath.join(base_cwd, p)
    return posixpath.normpath(p)


def exists(result: VResult, base_cwd: str, path: str) -> bool:
    p = resolve(result, base_cwd, path)
    kind = result.fs.get(p)
    if path.strip().endswith("/"):
        return kind == DIR
    return kind is not None


def listing(result: VResult, base: str) -> list[str]:
    """列出 base 底下所有東西（相對路徑，資料夾結尾加 /）。"""
    base = posixpath.normpath(base)
    out = []
    for p, kind in sorted(result.fs.items()):
        if p == base or not p.startswith(base.rstrip("/") + "/"):
            continue
        rel = posixpath.relpath(p, base)
        out.append(rel + "/" if kind == DIR else rel)
    return out


def diff(a: VResult, b: VResult, base: str) -> tuple[list[str], list[str]]:
    """比較兩個結果（從 base 看）：回傳 (a 有 b 沒有, b 有 a 沒有)。"""
    def rels(r: VResult) -> set[str]:
        out = set()
        for p, kind in r.fs.items():
            if p == "/":
                continue
            rel = posixpath.relpath(p, base)
            out.add(rel + "/" if kind == DIR else rel)
        return out

    ra, rb = rels(a), rels(b)
    return sorted(ra - rb), sorted(rb - ra)
