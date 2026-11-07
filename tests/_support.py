"""測試共用：假的家目錄、假的帳本、執行 check.py。

所有測試檔都寫在 PLUSFORM_TEST_WS 指定的資料夾（沒設就用系統暫存資料夾），
絕不寫到真的家目錄，也不寫課程資料夾。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

COURSE = Path(__file__).resolve().parent.parent
_ws = os.environ.get("PLUSFORM_TEST_WS")
WS = Path(_ws) if _ws else Path(tempfile.mkdtemp(prefix="plusform-test-"))
WS.mkdir(parents=True, exist_ok=True)

if str(COURSE) not in sys.path:
    sys.path.insert(0, str(COURSE))


def find_uv() -> str | None:
    env_uv = os.environ.get("UV")
    if env_uv and Path(env_uv).is_file():
        return env_uv
    return shutil.which("uv")


UV = find_uv()


def _uv_default(args: list[str]) -> str | None:
    """在換掉 HOME 之前，先問 uv 它平常的快取放哪裡，讓測試沿用（不重新下載 Python）。"""
    if not UV:
        return None
    try:
        out = subprocess.run([UV, *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() or None


UV_CACHE = os.environ.get("UV_CACHE_DIR") or _uv_default(["cache", "dir"]) or str(WS / "uv-cache")
UV_PYTHON = os.environ.get("UV_PYTHON_INSTALL_DIR") or _uv_default(["python", "dir"]) or str(WS / "uv-python")
UV_PYTHON_BIN = os.environ.get("UV_PYTHON_BIN_DIR") or str(WS / "uv-bin")


def fresh_dir(name: str) -> Path:
    path = WS / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def make_env(home: Path, now: str | None = None) -> dict:
    env = dict(os.environ)
    for key in ("PLUSFORM_PREDICT", "PLUSFORM_NOW", "VIRTUAL_ENV", "XDG_CONFIG_HOME", "PYPY_LEDGER_FILE"):
        env.pop(key, None)
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["APPDATA"] = str(home / "AppData" / "Roaming")
    env["PLUSFORM_CONFIG_DIR"] = str(home / ".config" / "plusform-course")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["UV_CACHE_DIR"] = UV_CACHE
    env["UV_PYTHON_INSTALL_DIR"] = UV_PYTHON
    env["UV_PYTHON_BIN_DIR"] = UV_PYTHON_BIN
    env["UV_NO_CONFIG"] = "1"
    env["TMPDIR"] = str(WS / "tmp")
    (WS / "tmp").mkdir(exist_ok=True)
    if now:
        env["PLUSFORM_NOW"] = now
    return env


def run_check(args: list[str], env: dict, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(COURSE / "check.py"), *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(COURSE),
        env=env,
        timeout=600,
    )


def uv_ledger(path: Path, package: bool = False) -> Path:
    """建一個真的 uv 帳本（跟學員在 0-5 做的一樣），在目前這個程序的環境裡。"""
    from engine import grader

    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    env = grader.child_env()
    layout = "--package" if package else "--no-package"
    subprocess.run([UV, "init", layout, "--vcs", "none", "--name", "ledger", "--quiet"], cwd=path, env=env, check=True)
    subprocess.run([UV, "python", "pin", "3.13", "--quiet"], cwd=path, env=env, check=True)
    if not package:
        subprocess.run([UV, "run", "--quiet", "main.py"], cwd=path, env=env, check=True, capture_output=True)
    return path


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    """在帳本裡跑 git（測試用的名字和信箱，不碰真的設定）。"""
    cmd = ["git", "-c", "user.name=PyPy Bear", "-c", "user.email=bear@example.com", "-c", "init.defaultBranch=main", *args]
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True, check=True)


def snapshot(root: Path) -> dict[str, tuple[int, int]]:
    out = {}
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        st = path.stat()
        out[path.relative_to(root).as_posix()] = (st.st_size, st.st_mtime_ns if path.is_file() else 0)
    return out
