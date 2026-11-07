"""PyPy 熊的記帳小幫手

一支在終端機裡用的記帳程式。

功能：
    1. 記一筆花費（日期、項目、分類、金額）
    2. 列出所有花費
    3. 依分類加總，並顯示占比
    4. 分帳（零頭也分好，加總一定等於原金額）
    5. 存檔與讀檔（文字檔，一行一筆，欄位用 Tab 隔開）

使用方式：
    uv run ledger_app.py
"""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# 資料檔放在家目錄
DATA_FILE = Path.home() / ".pypy_ledger.txt"

CATEGORIES = ["餐飲", "交通", "娛樂", "日用品", "其他"]
BAR_WIDTH = 20


class InvalidAmountError(Exception):
    """金額不合法時丟出的錯誤。"""


@dataclass
class Entry:
    """一筆花費。"""

    day: str
    item: str
    category: str
    amount: int

    def to_line(self, index: int) -> str:
        """把這筆花費排成一行，方便列印。"""
        return f"{index:>3}. {self.day}  {self.item:<10} {self.category:<4} {self.amount:>8,} 元"


@dataclass
class Ledger:
    """整本帳本，裡面放很多筆 Entry。"""

    entries: list[Entry] = field(default_factory=list)

    def add(self, entry: Entry) -> None:
        self.entries.append(entry)

    def total(self) -> int:
        return sum(entry.amount for entry in self.entries)

    def by_category(self) -> dict[str, int]:
        """依分類加總，金額大的排前面。"""
        totals: dict[str, int] = {}
        for entry in self.entries:
            totals[entry.category] = totals.get(entry.category, 0) + entry.amount
        return dict(sorted(totals.items(), key=lambda pair: pair[1], reverse=True))

    def save(self, path: Path = DATA_FILE) -> None:
        """一行一筆：日期、項目、分類、金額，中間用 Tab 隔開。"""
        with open(path, "w", encoding="utf-8") as f:
            for entry in self.entries:
                f.write(f"{entry.day}\t{entry.item}\t{entry.category}\t{entry.amount}\n")


def load_ledger(path: Path = DATA_FILE) -> Ledger:
    """從文字檔讀回帳本；檔案不存在就給一本空的。"""
    ledger = Ledger()
    if not path.exists():
        return ledger
    with open(path, encoding="utf-8") as f:
        for line in f:
            day, item, category, amount = line.rstrip("\n").split("\t")
            ledger.add(Entry(day, item, category, int(amount)))
    return ledger


def parse_amount(text: str) -> int:
    """把使用者輸入的金額轉成整數元。

    支援「120」「120元」「NT$1,200」這幾種寫法。
    """
    cleaned = text.strip().upper()
    for token in ("NT$", "$", ",", "元"):
        cleaned = cleaned.replace(token, "")
    amount = int(cleaned)
    if amount <= 0:
        raise InvalidAmountError("金額要大於 0")
    return amount


def split_bill(total: int, people: int) -> list[int]:
    """把 total 元分給 people 個人。

    每人相差不超過 1 元，零頭從第一個人開始多付 1 元，加總一定等於 total。
    """
    if people <= 0:
        raise ValueError("人數至少要 1 人")
    base, remainder = divmod(total, people)
    return [base + 1 if i < remainder else base for i in range(people)]


def ask_date() -> str:
    while True:
        text = input("日期（例如 2026-11-08，直接按 Enter 用今天）：").strip()
        if not text:
            return date.today().isoformat()
        try:
            return date.fromisoformat(text).isoformat()
        except ValueError:
            print("  日期格式要像 2026-11-08，請再輸入一次。")


def ask_category() -> str:
    for number, name in enumerate(CATEGORIES, start=1):
        print(f"  {number}. {name}")
    choice = input("分類（輸入編號）：").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
        return CATEGORIES[int(choice) - 1]
    print("  沒有這個編號，先放進「其他」。")
    return "其他"


def cmd_add(ledger: Ledger) -> None:
    day = ask_date()
    item = input("項目：").strip() or "未命名"
    category = ask_category()
    while True:
        try:
            amount = parse_amount(input("金額："))
            break
        except InvalidAmountError as error:
            print(f"  {error}，請再輸入一次。")
    ledger.add(Entry(day, item, category, amount))
    print(f"  已記下：{item} {amount:,} 元")


def cmd_list(ledger: Ledger) -> None:
    if not ledger.entries:
        print("  帳本是空的，先記一筆吧。")
        return
    for index, entry in enumerate(ledger.entries, start=1):
        print(entry.to_line(index))
    print(f"  共 {len(ledger.entries)} 筆，合計 {ledger.total():,} 元")


def cmd_summary(ledger: Ledger) -> None:
    total = ledger.total()
    if total == 0:
        print("  還沒有花費可以加總。")
        return
    for category, amount in ledger.by_category().items():
        ratio = amount / total
        bar = "█" * round(ratio * BAR_WIDTH)
        print(f"  {category:<4} {amount:>8,} 元  {ratio:>6.1%}  {bar}")
    print(f"  {'合計':<4} {total:>8,} 元")


def cmd_split(ledger: Ledger) -> None:
    total = parse_amount(input("要分的總金額："))
    try:
        people = int(input("幾個人分："))
        shares = split_bill(total, people)
    except ValueError as error:
        print(f"  沒辦法分帳：{error}")
        return
    for number, share in enumerate(shares, start=1):
        print(f"  第 {number} 個人付 {share:,} 元")
    print(f"  加總 {sum(shares):,} 元（應該等於 {total:,} 元）")


def cmd_save(ledger: Ledger) -> None:
    ledger.save()
    print(f"  已存到 {DATA_FILE}")


def cmd_load(ledger: Ledger) -> None:
    loaded = load_ledger()
    ledger.entries = loaded.entries
    print(f"  從 {DATA_FILE} 讀回 {len(ledger.entries)} 筆")


MENU = {
    "1": ("記一筆", cmd_add),
    "2": ("列出所有花費", cmd_list),
    "3": ("分類加總", cmd_summary),
    "4": ("分帳", cmd_split),
    "5": ("存檔", cmd_save),
    "6": ("讀檔", cmd_load),
}


def main() -> None:
    ledger = load_ledger()
    print("=== PyPy 熊的記帳小幫手 ===")
    if ledger.entries:
        print(f"讀到 {len(ledger.entries)} 筆舊紀錄。")
    while True:
        print()
        for key, (label, _action) in MENU.items():
            print(f"  {key}. {label}")
        print("  q. 存檔並離開")
        choice = input("請選擇：").strip().lower()
        if choice == "q":
            ledger.save()
            print("已存檔，下次見！")
            break
        if choice not in MENU:
            print("沒有這個選項，請再選一次。")
            continue
        _label, action = MENU[choice]
        action(ledger)


if __name__ == "__main__":
    main()
