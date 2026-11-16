def to_yuan(text):
    text = text.replace(",", "")
    text = text.replace("元", "")
    return int(text)


if __name__ == "__main__":
    print(to_yuan("1,200"))
    print(to_yuan("一百"))
