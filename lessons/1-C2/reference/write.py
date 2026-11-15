amount = int(input("金額："))
if amount >= 1000:
    fee = 0
elif amount >= 500:
    fee = 60
else:
    fee = 100
print(f"運費 {fee} 元，一共 {amount + fee} 元")
