"""帳本 v1.0：第 1 級的最後一版（1-27 第一部分：手寫，全程關掉 AI）

一筆帳有四個欄位：日期、項目、分類、金額。帳本檔 ledger_v1.txt 跟這個檔放在同一個資料夾，
一行一筆，欄位用逗號隔開，例如：11/03,午餐,餐飲,120

你要寫的有五樣：Entry、to_yuan、load、save、totals（規格寫在每一樣上面的註解和 docstring 裡）。
最下面的 main() 是課程寫好的選單，不用改；五樣都寫好，在帳本資料夾打
uv run lessons/1-27/ledger_v1.py 就能記帳了。
"""
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).parent / "ledger_v1.txt"

# 1. Entry：用 @dataclass 寫，四個欄位照這個順序：date（文字）、item（文字）、category（文字）、amount（整數）


def to_yuan(text: str) -> int:
    """2. 把打進來的金額變成整數元。

    輸入：text，例如 "120"、"120元"、"1,200"
    輸出：整數，例如 1200
    規則：先拿掉逗號和「元」，再變成整數；變不成整數的（例如 "八十"），讓 int 丟出的 ValueError 丟出去；
          小於或等於 0 的，raise ValueError，錯誤訊息裡要有 text
    例子：to_yuan("1,200元") 是 1200
    """


def load(path: Path) -> list:
    """3. 讀回帳本檔，交回一串 Entry（金額是整數）。

    輸入：path，帳本檔的路徑（用 encoding="utf-8" 打開）
    輸出：一串 Entry，照檔案裡的順序；檔案不存在，交回空的 list
    例子：檔案裡只有 11/03,午餐,餐飲,120 這一行，load(path) 是 [Entry("11/03", "午餐", "餐飲", 120)]
    """


def save(path: Path, entries: list) -> None:
    """4. 把 entries 存進 path：整個檔案重寫，encoding="utf-8"，一行一筆，每一行後面都換行。

    例子：save(path, [Entry("11/03", "午餐", "餐飲", 120)]) 以後，檔案裡是 11/03,午餐,餐飲,120 這一行
    """


def totals(entries: list) -> dict:
    """5. 依分類加總，交回 {分類: 合計}，分類照第一次出現的順序。沒有帳交回空的 dict。

    例子：三筆 午餐 餐飲 120、公車 交通 15、晚餐 餐飲 180，totals 是 {"餐飲": 300, "交通": 15}
    """


# ---------- 下面是課程寫好的選單（不用改）----------
def main():
    entries = load(DATA)
    print(f"=== 帳本 v1.0（讀到 {len(entries)} 筆）===")
    while True:
        choice = input("1 記一筆　2 分類加總　q 存檔離開：").strip()
        if choice == "q":
            save(DATA, entries)
            print(f"存好了，一共 {len(entries)} 筆。")
            break
        if choice == "1":
            date = input("日期：").strip()
            item = input("項目：").strip()
            category = input("分類：").strip()
            while True:
                try:
                    amount = to_yuan(input("金額："))
                    break
                except ValueError:
                    print("  看不懂這個金額，請再打一次。")
            entries.append(Entry(date, item, category, amount))
            print(f"  記下了：{item} {amount} 元")
        elif choice == "2":
            for name, money in totals(entries).items():
                print(f"  {name} {money} 元")
        else:
            print("  沒有這個選項。")


if __name__ == "__main__":
    main()
