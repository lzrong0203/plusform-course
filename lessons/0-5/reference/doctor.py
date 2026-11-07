"""帳本健康檢查：印出現在用的是哪一個 Python（正確版）。

這支是給你跑的，不是給你讀的；看不懂裡面在寫什麼很正常。
"""

import sys
from pathlib import Path

version = f"{sys.version_info.major}.{sys.version_info.minor}"
print(f"Python 版本：{version}")

venv = Path(sys.prefix).resolve()
ledger = Path.cwd().resolve()
in_ledger = venv == ledger / ".venv"
print("在帳本的環境裡：" + ("是" if in_ledger else "否"))

base = Path(sys.base_prefix).resolve().as_posix()
is_system = base == "/usr" or base.startswith("/System/") or base.startswith("/Library/Developer/") or base.startswith("/Applications/Xcode")
print("用的是系統 Python：" + ("是" if is_system else "否"))
