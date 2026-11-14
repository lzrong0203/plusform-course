"""設定檔與學員帳本裡的紀錄（ledger/.check/）。

規則：課程資料夾裡什麼都不寫。
- 帳本在哪裡，記在使用者設定檔：
    Mac／Linux：~/.config/plusform-course/config.json（有 XDG_CONFIG_HOME 就用它）
    Windows：%APPDATA%\\plusform-course\\config.json
  環境變數 PLUSFORM_CONFIG_DIR 可以換掉這個資料夾（測試一律用它）。
- 進度、預測、校準、回顧紀錄都寫在 <帳本>/.check/。

只用 Python 標準庫。
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

CONFIG_ENV = "PLUSFORM_CONFIG_DIR"
NOW_ENV = "PLUSFORM_NOW"  # 測試用：假裝現在是某個時間（ISO 格式）
CHECK_DIR = ".check"


def now() -> datetime:
    raw = os.environ.get(NOW_ENV)
    if raw:
        value = datetime.fromisoformat(raw)
        return value if value.tzinfo else value.astimezone()
    return datetime.now().astimezone()


def parse_time(text: str) -> datetime:
    value = datetime.fromisoformat(text)
    return value if value.tzinfo else value.astimezone()


def day_of(text: str) -> str:
    return parse_time(text).date().isoformat()


def config_dir() -> Path:
    override = os.environ.get(CONFIG_ENV)
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        root = Path(base) if base else Path.home() / "AppData" / "Roaming"
    else:
        base = os.environ.get("XDG_CONFIG_HOME")
        root = Path(base) if base else Path.home() / ".config"
    return root / "plusform-course"


def config_path() -> Path:
    return config_dir() / "config.json"


def load_config() -> dict | None:
    path = config_path()
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save_config(data: dict) -> Path:
    path = config_path()
    _atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return path


def ledger_from_config() -> Path | None:
    cfg = load_config()
    if not cfg or not cfg.get("ledger"):
        return None
    return Path(cfg["ledger"])


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


class Records:
    """<帳本>/.check/ 裡的紀錄。"""

    def __init__(self, ledger: Path):
        self.ledger = ledger
        self.dir = ledger / CHECK_DIR

    def ensure(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        readme = self.dir / "README.txt"
        if not readme.exists():
            readme.write_text(
                "這個資料夾是 check.py 記錄進度用的：\n"
                "  progress.json   每一課的進度\n"
                "  attempts.jsonl  每次檢查的結果和你猜的分數（校準曲線用）\n"
                "  reviews.jsonl   回顧題的作答\n"
                "  notes.jsonl     你寫的「下次我會怎麼估」\n"
                "不要刪；刪掉的話進度就不見了。\n",
                encoding="utf-8",
            )
        # 0-7 起帳本是 git 存放庫：進度紀錄每跑一次 check.py 就會變，不放進存檔點（不然原始碼控制一直冒出改動，
        # 按 Discard 也可能把進度退回去）。跟 uv 在 .venv 裡放的 .gitignore 一樣，只寫一個 *。
        ignore = self.dir / ".gitignore"
        if not ignore.exists():
            ignore.write_text("# check.py 的進度紀錄不放進 git 的存檔點\n*\n", encoding="utf-8")

    # ---------- progress.json ----------
    def progress(self) -> dict:
        path = self.dir / "progress.json"
        if not path.is_file():
            return {"version": 1, "lessons": {}, "frontier": -1}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("lessons", {}), dict):
                data.setdefault("lessons", {})
                data.setdefault("frontier", -1)
                return data
        except (ValueError, UnicodeDecodeError):
            pass
        # 壞掉了：不要默默清空。先改名留著，再照 attempts.jsonl 盡量補回來。
        broken = path.with_name(f"progress.json.broken-{now().strftime('%Y%m%d-%H%M%S')}")
        try:
            os.replace(path, broken)
            kept = f"已經改名成 {broken.name} 留著"
        except OSError:
            kept = "沒辦法改名"
        data = self.rebuild_progress()
        print(f"（你的進度檔 {path} 壞掉了，{kept}；先照檢查紀錄 attempts.jsonl 把每一課的進度補回來。）")
        self.save_progress(data)
        return data

    def rebuild_progress(self) -> dict:
        lessons: dict[str, dict] = {}
        for a in self.read("attempts"):
            lid = a.get("lesson")
            if not lid or not a.get("time"):
                continue
            info = lessons.setdefault(lid, {"first_run": a["time"], "runs": 0})
            info["runs"] += 1
            info["last_run"] = a["time"]
            info["last_result"] = [a.get("passed", 0), a.get("total", 0)]
            if a.get("total") and a.get("passed") == a.get("total"):
                info.setdefault("first_pass", a["time"])
        return {"version": 1, "lessons": lessons, "frontier": -1, "rebuilt": True}

    def save_progress(self, data: dict) -> None:
        self.ensure()
        _atomic_write(self.dir / "progress.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    # ---------- *.jsonl ----------
    def append(self, name: str, record: dict) -> None:
        self.ensure()
        with open(self.dir / f"{name}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def read(self, name: str) -> list[dict]:
        path = self.dir / f"{name}.jsonl"
        if not path.is_file():
            return []
        out = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
        return out
