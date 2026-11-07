"""在學員帳本的 Python 環境裡執行的小幫手（由 check.py 用 subprocess 呼叫）。

check.py 把要做的事用 JSON 從 stdin 傳進來（裡面有一個每次都不一樣的暗號 token），
這支程式做完之後，把結果用 JSON 印在最後一行（前面加上標記和暗號）。
學員程式自己 print 的東西會被丟掉，不會混進結果，也不會把記憶體吃光。

做這幾件事：
- call：載入一個 .py 檔，呼叫裡面的函式，比對回傳值
- load：只載入一個 .py 檔，看會不會一載入就出錯（老師端驗證壞版本用）
- asserts：把學員寫的 assert 一條一條拿去跑「一個」版本（正確版或某一個壞版本）。
  每個版本各開一個程序跑，版本之間不會互相影響；一個版本卡住，也不會拖累別的版本。
- probe：回報現在用的是哪一個 Python

跑 assert 之前會先印一行「進度」，這樣卡在無窮迴圈被收掉的時候，check.py 知道卡在哪一行。

只用 Python 標準庫；不寫任何檔案（也不寫 __pycache__）。
"""

import ast
import contextlib
import importlib.util
import io
import json
import sys
import traceback
from pathlib import Path

sys.dont_write_bytecode = True

MARK = "@@PLUSFORM@@"
OUTPUT_CAP = 2_000_000  # 學員程式最多印這麼多字，再多就停下來
_REAL_STDOUT = sys.stdout
_TOKEN = ""


class TooMuchOutput(BaseException):
    """學員程式印太多了（用 BaseException，學員的 except Exception 接不住）。"""


class _Sink(io.TextIOBase):
    """收學員印出來的東西：只數字數、不留內容，超過上限就叫停。"""

    def __init__(self):
        self.count = 0

    def writable(self):
        return True

    def write(self, text):
        self.count += len(text)
        if self.count > OUTPUT_CAP:
            raise TooMuchOutput("印太多了（可能是迴圈沒停下來）")
        return len(text)


def emit(kind: str, payload) -> None:
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    _REAL_STDOUT.write(f"\n{MARK}{_TOKEN}@@{kind} {text}\n")
    _REAL_STDOUT.flush()


def short_error(exc: BaseException) -> str:
    text = str(exc)
    name = type(exc).__name__
    return f"{name}: {text}" if text else name


def error_line(exc: BaseException, filename: str):
    """找出錯誤發生在 filename 的第幾行。"""
    target = str(Path(filename).resolve())
    for frame in reversed(traceback.extract_tb(exc.__traceback__)):
        try:
            if frame.filename == filename or str(Path(frame.filename).resolve()) == target:
                return frame.lineno
        except OSError:
            continue
    return None


@contextlib.contextmanager
def quiet():
    """把學員程式印出來的東西收起來（有上限），也不讓它讀鍵盤。"""
    sink = _Sink()
    old_in = sys.stdin
    sys.stdin = io.StringIO("")
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            yield sink
    finally:
        sys.stdin = old_in


def load_module(name: str, path: str):
    sys.modules.pop(name, None)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"載入不了 {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    with quiet():
        spec.loader.exec_module(module)
    return module


def describe_load_error(exc: BaseException, path: str) -> dict:
    if isinstance(exc, SyntaxError):
        msg = exc.msg
        if "utf-8" in str(exc).lower() or "non-utf-8" in msg.lower():
            return {"kind": "encoding", "line": exc.lineno, "msg": msg}
        return {"kind": "syntax", "line": exc.lineno, "msg": msg}
    if isinstance(exc, EOFError):
        return {"kind": "input", "line": error_line(exc, path), "msg": short_error(exc)}
    return {"kind": "crash", "line": error_line(exc, path), "msg": short_error(exc)}


def _add_path(filename: str) -> None:
    folder = str(Path(filename).resolve().parent)
    if folder not in sys.path:
        sys.path.insert(0, folder)


def _jsonable(value) -> bool:
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False


def op_call(req: dict) -> dict:
    path = req["file"]
    _add_path(path)
    out = {"load_error": None, "cases": []}
    try:
        module = load_module(req["module"], path)
    except BaseException as exc:  # noqa: BLE001 - 學員程式什麼錯都可能有
        out["load_error"] = describe_load_error(exc, path)
        return out
    func = getattr(module, req["func"], None)
    if not callable(func):
        out["load_error"] = {"kind": "missing", "line": None, "msg": req["func"]}
        return out
    for i, case in enumerate(req["cases"]):
        emit("progress", f"case {i}")
        try:
            with quiet():
                got = func(*case.get("args", []))
            out["cases"].append({"ok": got == case["expect"], "got": got if _jsonable(got) else repr(got)})
        except BaseException as exc:  # noqa: BLE001
            out["cases"].append({"ok": False, "error": short_error(exc), "line": error_line(exc, path)})
    return out


def op_load(req: dict) -> dict:
    path = req["file"]
    _add_path(path)
    try:
        module = load_module(req["module"], path)
    except BaseException as exc:  # noqa: BLE001
        return {"load_error": describe_load_error(exc, path)}
    names = [n for n in vars(module) if not n.startswith("_")]
    return {"load_error": None, "names": names}


def _value_text(node, ns, filename):
    try:
        code = compile(ast.Expression(node), filename, "eval")
        with quiet():
            value = eval(code, ns)  # noqa: S307 - 這就是要跑學員寫的運算式
        return value if _jsonable(value) else repr(value)
    except BaseException:  # noqa: BLE001
        return None


def op_asserts(req: dict) -> dict:
    filename = req["checks_file"]
    _add_path(filename)
    try:
        source = Path(filename).read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return {"encoding": True}
    try:
        tree = ast.parse(source, filename)
    except SyntaxError as exc:
        return {"syntax": {"line": exc.lineno, "msg": exc.msg}}
    impl = req["impl"]
    entry = {"load_error": None, "asserts": [], "setup_error": None}
    emit("start", "load")
    try:
        load_module(req["module"], impl)
    except BaseException as exc:  # noqa: BLE001
        entry["load_error"] = short_error(exc)
    ns = {"__name__": "__plusform_checks__", "__file__": filename}
    for stmt in tree.body:
        code = compile(ast.Module(body=[stmt], type_ignores=[]), filename, "exec")
        broken = entry["load_error"] or entry["setup_error"]
        if isinstance(stmt, ast.Assert):
            rec = {"line": stmt.lineno}
            if broken:
                rec.update(status="error", error=broken, skipped=True)
            else:
                emit("start", f"assert {stmt.lineno}")
                try:
                    with quiet():
                        exec(code, ns)  # noqa: S102
                    rec["status"] = "pass"
                except AssertionError:
                    rec["status"] = "fail"
                    test = stmt.test
                    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
                        rec["got"] = _value_text(test.left, ns, filename)
                except BaseException as exc:  # noqa: BLE001
                    rec.update(status="error", error=short_error(exc))
            entry["asserts"].append(rec)
            emit("done", rec)
        elif not broken:
            emit("start", f"stmt {stmt.lineno}")
            try:
                with quiet():
                    exec(code, ns)  # noqa: S102
            except BaseException as exc:  # noqa: BLE001
                entry["setup_error"] = f"第 {stmt.lineno} 行就出錯了：{short_error(exc)}"
                entry["setup_line"] = stmt.lineno
    return entry


def op_probe(_req: dict) -> dict:
    return {
        "executable": sys.executable,
        "prefix": sys.prefix,
        "base_prefix": sys.base_prefix,
        "version": list(sys.version_info[:3]),
    }


OPS = {"call": op_call, "load": op_load, "asserts": op_asserts, "probe": op_probe}


def main() -> None:
    global _TOKEN
    try:
        req = json.loads(sys.stdin.read() or "{}")
        _TOKEN = str(req.get("token", ""))
        sys.stdin = io.StringIO("")
        result = OPS[req["op"]](req)
    except BaseException as exc:  # noqa: BLE001
        result = {"runner_error": short_error(exc)}
    emit("result", result)


if __name__ == "__main__":
    main()
