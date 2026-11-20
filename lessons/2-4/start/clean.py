# 2-4 第①圈：對帳單的字，整理成帳本要的樣子
import re


def roc_date(text):
    """民國年的日期換成西元年：115/11/03 → 2026/11/03"""
    m = re.fullmatch(r"(\d{2,3})/(\d{1,2})/(\d{1,2})", text.strip())
    if m is None:
        raise ValueError(f"看不懂的日期：{text}")
    year = int(m.group(1)) + 1911
    return f"{year}/{int(m.group(2)):02d}/{int(m.group(3)):02d}"


def to_int(text):
    """金額的字換成整數：1,250 → 1250，-350 → -350（退款是負的）"""
    return int(text)   # 換你改：先拿掉千分位的逗號
