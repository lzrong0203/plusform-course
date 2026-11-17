"""帳本 v1.0：第 1 級的最後一版（1-27 卷 B 第一部分：手寫的參考寫法；寫法不只一種，check 照跑出來的結果判）

這一版的帳本會記「誰付的」：一筆帳有四個欄位：日期、項目、金額、誰付的。帳本檔 ledger_v1.txt 跟這個檔放在同一個資料夾，
一行一筆，欄位用逗號隔開，例如：11/03,午餐,120,熊

你要寫的有五樣：Entry、to_yuan、load、save、by_payer（規格寫在每一樣上面的註解和 docstring 裡）。
最下面的 main() 是課程寫好的選單，不用改；五樣都寫好，在帳本資料夾打
uv run lessons/1-27B/ledger_v1.py 就能記帳了。
"""
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).parent / "ledger_v1.txt"

# 1. Entry：用 @dataclass 寫，四個欄位照這個順序：date（文字）、item（文字）、amount（整數）、payer（文字，誰付的）
@dataclass
class Entry:
    date: str
    item: str
    amount: int
    payer: str


def to_yuan(text: str) -> int:
    """2. 把打進來的金額變成整數元。

    輸入：text，例如 "65"、"65元"、"3,500"
    輸出：整數，例如 3500
    規則：先拿掉逗號和「元」，再變成整數；變不成整數的（例如 "兩百"），讓 int 丟出的 ValueError 丟出去；
          小於或等於 0 的，raise ValueError，錯誤訊息裡要有 text
    例子：to_yuan("3,500元") 是 3500
    """
    amount = int(text.replace(",", "").replace("元", ""))
    if amount <= 0:
        raise ValueError(f"金額要大於 0：{text}")
    return amount


def load(path: Path) -> list:
    """3. 讀回帳本檔，交回一串 Entry（金額是整數）。

    輸入：path，帳本檔的路徑（用 encoding="utf-8" 打開）
    輸出：一串 Entry，照檔案裡的順序；檔案不存在，交回空的 list
    例子：檔案裡只有 11/03,午餐,120,熊 這一行，load(path) 是 [Entry("11/03", "午餐", 120, "熊")]
    """
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            date, item, amount, payer = line.rstrip("\n").split(",")
            entries.append(Entry(date, item, int(amount), payer))
    return entries


def save(path: Path, entries: list) -> None:
    """4. 把 entries 存進 path：整個檔案重寫，encoding="utf-8"，一行一筆，每一行後面都換行。

    例子：save(path, [Entry("11/03", "午餐", 120, "熊")]) 以後，檔案裡是 11/03,午餐,120,熊 這一行
    """
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(f"{e.date},{e.item},{e.amount},{e.payer}\n")


def by_payer(entries: list) -> dict:
    """5. 每個人付了多少：交回 {誰付的: 合計}，人照第一次出現的順序。沒有帳交回空的 dict。

    例子：三筆 午餐 120 熊、公車 15 兔、晚餐 180 熊，by_payer 是 {"熊": 300, "兔": 15}
    """
    out = {}
    for e in entries:
        out[e.payer] = out.get(e.payer, 0) + e.amount
    return out


# ---------- 下面是課程寫好的選單（不用改）----------
def main():
    entries = load(DATA)
    print(f"=== 帳本 v1.0（讀到 {len(entries)} 筆）===")
    while True:
        choice = input("1 記一筆　2 誰付了多少　q 存檔離開：").strip()
        if choice == "q":
            save(DATA, entries)
            print(f"存好了，一共 {len(entries)} 筆。")
            break
        if choice == "1":
            date = input("日期：").strip()
            item = input("項目：").strip()
            while True:
                try:
                    amount = to_yuan(input("金額："))
                    break
                except ValueError:
                    print("  看不懂這個金額，請再打一次。")
            payer = input("誰付的：").strip()
            entries.append(Entry(date, item, amount, payer))
            print(f"  記下了：{item} {amount} 元（{payer}付）")
        elif choice == "2":
            for name, money in by_payer(entries).items():
                print(f"  {name} 付了 {money} 元")
        else:
            print("  沒有這個選項。")


if __name__ == "__main__":
    main()
