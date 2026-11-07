# /// script
# requires-python = ">=3.13"
# ///
"""跑課程資料夾自己的全部自動測試（老師用）。

在課程資料夾裡打：uv run tests/run_all.py
  - 這支有 PEP 723 標頭，uv 會用獨立的環境跑它，不會碰到上層專案的 .venv。
  - 一開頭就關掉 __pycache__，課程資料夾裡什麼都不寫。
加 -v 看每一條測試的名字；加 -k 名字 只跑名字有那幾個字的測試。
"""

import sys

sys.dont_write_bytecode = True

import unittest  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> int:
    args = sys.argv[1:]
    verbosity = 2 if "-v" in args else 1
    pattern = None
    if "-k" in args:
        i = args.index("-k")
        pattern = args[i + 1] if i + 1 < len(args) else None
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    loader = unittest.TestLoader()
    if pattern:
        loader.testNamePatterns = [f"*{pattern}*"]
    suite = loader.discover(start_dir=str(HERE), top_level_dir=str(HERE))
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
