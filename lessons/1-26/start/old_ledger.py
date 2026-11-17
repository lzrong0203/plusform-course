"""old_ledger.py：熊的舊記帳程式。

帳存在旁邊的 old_ledger.txt，一行一筆，例如 11/03 午餐 120。
跑起來以後打指令：show 列出每一筆、add 11/06 咖啡 85 記一筆、total 合計、q 離開。
"""
import logging
import re
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).parent / "old_ledger.txt"
LINE = re.compile(r"(\d+/\d+) (\S+) (\d+)")
COMMANDS = {}


@dataclass
class Entry:
    date: str
    item: str
    amount: int


def command(func):
    """把函式登記成一個指令，指令的名字就是函式的名字。"""
    COMMANDS[func.__name__] = func
    return func


def parse(text):
    """「11/03 午餐 120」→ Entry；格式不對就丟 ValueError。"""
    m = LINE.fullmatch(text.strip())
    if m is None:
        raise ValueError(f"看不懂：{text.strip()}")
    return Entry(m.group(1), m.group(2), int(m.group(3)))


def read_entries(path):
    """一次交出一筆 Entry；看不懂的那一行跳過。"""
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                yield parse(line)
            except ValueError:
                logging.warning(f"第 {n} 行看不懂，跳過")


def load():
    if not DATA.exists():
        return []
    entries = list(read_entries(DATA))
    logging.info(f"讀了 {len(entries)} 筆")
    return entries


def save(entries):
    with open(DATA, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(f"{e.date} {e.item} {e.amount}\n")


def fmt(no, e):
    return f"{no}. {e.date} {e.item} {e.amount}"


@command
def show(entries, arg):
    if not entries:
        print("（還沒有帳）")
    for no, e in enumerate(entries, start=1):
        print(fmt(no, e))


@command
def add(entries, arg):
    e = parse(arg)
    entries.append(e)
    save(entries)
    print("記好了：", fmt(len(entries), e))


@command
def total(entries, arg):
    print("合計", sum(e.amount for e in entries), "元")


def main():
    entries = load()
    print("可以打的指令：" + "、".join(COMMANDS) + "、q")
    while True:
        text = input("> ").strip()
        if text == "q":
            break
        words = text.split(" ", 1)
        name = words[0]
        arg = words[1] if len(words) == 2 else ""
        if name not in COMMANDS:
            print("沒有這個指令：", name)
            continue
        try:
            COMMANDS[name](entries, arg)
        except ValueError as err:
            logging.warning(err)


if __name__ == "__main__":
    main()
