# 1-19 第②圈：請家教解釋你踩到的範圍錯誤，再出一題考它

1. 在家教專案裡貼上你踩到的錯（scope.txt 第 3 題、你自己寫錯的程式，或下面這段）和錯誤訊息的最後一行，打：
   「外面明明有 count = 0，為什麼說找不到？請用問題帶我想，先不要給我改好的程式。」
2. 照家教的問題自己想、自己跑跑看，把你的理解講給它聽。
3. 換你出一題**同類型**的考它（函式裡外有同一個名字的題目），請它直接回答、說為什麼。
4. 家教的回答對不對，**自己跑一次**確定（AI 也會答錯）。

```python
count = 0

def add_entry(book, amount):
    book.append(amount)
    count = count + 1

nov = []
add_entry(nov, 120)
print(count)
```

錯誤訊息最後一行：`UnboundLocalError: cannot access local variable 'count' where it is not associated with a value`

每個標籤後面都要寫字（check 只看寫了沒，不改對錯）：

我踩到的錯：

家教問我的：

我的回答：

我出的題目：

家教的回答：

跑出來對不對：

自評（打勾）：

- [ ] 我說得出：函式裡給了值的名字，是小框自己的；外面同名的那個不會變
- [ ] 我說得出：函式裡先讀、後給值，就會出現 UnboundLocalError
- [ ] 要改外面的數字，我用參數交進去、用 return 交回來，不在函式裡偷改外面的
- [ ] 家教的回答，我自己跑過一次，確定它說得對不對
