amount = int(input("金額："))
if amount >= 2000:
    off = 200
elif amount >= 800:
    off = 50
else:
    off = 0
print(f"折 {off} 元，要付 {amount - off} 元")
