# 週末採買：算出總金額、每人要付多少
# 1. 三樣東西的單價和數量
milk_price = 85
milk_qty = 2
egg_price = 65
egg_qty = 1
bread_price = "45"
bread_qty = 3
# 2. 每一樣的小計
milk = milk_price * milk_qty
egg = egg_price * egg_qty
bread = bread_price * bread_qty
# 3. 總金額
total = milk + egg + bread
print(f"總金額 {total} 元")
# 4. 三個人平分
people = 3
each = total // people
rest = total % people
print(f"每人 {each} 元，零頭 {rest} 元")
