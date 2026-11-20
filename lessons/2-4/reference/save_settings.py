# 2-4 第①圈：把設定存成 JSON，再讀回來
import json
from pathlib import Path

settings = {
    "每月預算": 12000,
    "分類關鍵字": {"早餐店": "餐飲", "便當店": "餐飲", "捷運": "交通", "超市": "日用品", "電影院": "娛樂"},
}
p = Path(__file__).parent / "settings.json"
with open(p, "w", encoding="utf-8") as f:
    json.dump(settings, f, ensure_ascii=False, indent=2)

with open(p, encoding="utf-8") as f:
    back = json.load(f)
print("讀回來的每月預算：", back["每月預算"])
