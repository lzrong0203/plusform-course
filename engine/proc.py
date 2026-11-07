"""跑學員程式的共用零件：有時間上限、有輸出上限，時間到就連子程序一起收掉。

為什麼不用 subprocess.run(timeout=…)：
- 它逾時只殺得到「直接開的那一個程序」。學員程式如果又開了子程序（或是透過 uv 這類
  會再開一層的工具），孫程序會變成孤兒，一直吃 CPU。
- 它會把輸出整份收進記憶體。學員程式狂印的時候，check.py 自己的記憶體會爆。

所以這裡改用 Popen：
- Mac／Linux 開新的程序群組（start_new_session），收掉時整個群組一起殺。
- Windows 開新的程序群組，收掉時用 taskkill /T /F 把整棵樹殺掉。
- stdout／stderr 用執行緒分塊讀，超過上限就收掉程式、只留前面一段。
- stdin 由這裡餵（不靠 shell 的 <），Mac 和 Windows 都一樣。

只用 Python 標準庫。
"""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass

DEFAULT_CAP = 1_000_000  # 每個輸出最多留 1 MB
CHUNK = 65536


@dataclass
class Proc:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    overflow: bool = False  # 印太多，被收掉了

    @property
    def stopped(self) -> bool:
        """被 check.py 收掉的（跑太久或印太多）。"""
        return self.timed_out or self.overflow


class _Reader(threading.Thread):
    def __init__(self, stream, cap: int, too_much: threading.Event):
        super().__init__(daemon=True)
        self.stream = stream
        self.cap = cap
        self.too_much = too_much
        self.parts: list[bytes] = []
        self.size = 0

    def run(self) -> None:
        try:
            while True:
                chunk = self.stream.read1(CHUNK) if hasattr(self.stream, "read1") else self.stream.read(CHUNK)
                if not chunk:
                    break
                keep = chunk[: max(self.cap - self.size, 0)]
                if keep:
                    self.parts.append(keep)
                    self.size += len(keep)
                if len(keep) < len(chunk):  # 有東西被丟掉了：印太多
                    self.too_much.set()
        except (OSError, ValueError):
            pass

    def text(self) -> str:
        return b"".join(self.parts).decode("utf-8", errors="replace")


def _feed(stream, data: bytes) -> None:
    try:
        if data:
            stream.write(data)
            stream.flush()
    except (BrokenPipeError, OSError, ValueError):
        pass
    finally:
        try:
            stream.close()
        except OSError:
            pass


def kill_tree(proc: subprocess.Popen) -> None:
    """把這個程序和它開出來的所有子程序一起收掉。"""
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        except (OSError, subprocess.SubprocessError):
            pass
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
    try:
        proc.kill()
    except OSError:
        pass


def run(cmd: list[str], *, stdin: str = "", cwd: str | os.PathLike | None = None, env: dict | None = None,
        timeout: float = 30.0, cap: int = DEFAULT_CAP) -> Proc:
    kwargs: dict = {}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            cwd=None if cwd is None else str(cwd), env=env, **kwargs)
    too_much = threading.Event()
    out = _Reader(proc.stdout, cap, too_much)
    err = _Reader(proc.stderr, cap, too_much)
    feeder = threading.Thread(target=_feed, args=(proc.stdin, stdin.encode("utf-8")), daemon=True)
    for t in (out, err, feeder):
        t.start()

    deadline = time.monotonic() + timeout
    timed_out = overflow = False
    try:
        while True:
            try:
                proc.wait(timeout=0.05)
                break
            except subprocess.TimeoutExpired:
                pass
            if too_much.is_set():
                overflow = True
                kill_tree(proc)
                break
            if time.monotonic() >= deadline:
                timed_out = True
                kill_tree(proc)
                break
    except BaseException:
        # 學員在等的時候按 Ctrl+C（或關掉視窗）：學員程式在新的程序群組，收不到終端機的 Ctrl+C，
        # 不先整群收掉就會變成背景一直跑的孤兒程序（1-10 的無窮迴圈最容易遇到）
        kill_tree(proc)
        raise

    # 程式結束了，可是它開的子程序可能還拿著輸出管道：等一下下，還沒讀完就整群收掉
    for t in (out, err):
        t.join(timeout=1.0)
    if out.is_alive() or err.is_alive():
        kill_tree(proc)
        for t in (out, err):
            t.join(timeout=2.0)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    for stream in (proc.stdout, proc.stderr):
        try:
            stream.close()
        except OSError:
            pass
    code = proc.returncode if proc.returncode is not None else -1
    return Proc(code, out.text(), err.text(), timed_out=timed_out and not overflow,
                overflow=overflow or too_much.is_set())
